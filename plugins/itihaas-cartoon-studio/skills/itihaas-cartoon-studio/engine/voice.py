"""Records narration per beat. python voice.py <project> [--force]

FREE: Microsoft Edge neural voices (edge-tts), default hi-IN-MadhurNeural.
PAID: ElevenLabs (voice.engine = "elevenlabs", key in env ELEVENLABS_API_KEY).
OWN:  voice.engine = "own" -> put your recordings in audio/own/<beat id>.mp3|wav (or one file
      audio/own/full.wav plus "own_cuts" in story.json, see references/voice.md).

Writes audio/beats/<id>.wav (44.1 kHz mono), audio/env/<id>.npy (mouth envelope at 30 fps) and
audio/timing.json. Only changed beats are re-recorded.
"""
import os, sys, json, hashlib, asyncio, ssl, subprocess, wave
import numpy as np
from common import load_json, save_json, ffmpeg_bin

FPS = 30


def _ssl_ctx():
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except Exception:
        pass
    for p in (os.environ.get("SSL_CERT_FILE"), os.environ.get("REQUESTS_CA_BUNDLE"), "/root/.ccr/ca-bundle.crt"):
        if p and os.path.exists(p):
            try:
                ctx.load_verify_locations(p)
            except Exception:
                pass
    return ctx


async def _edge(text, voice, rate, pitch, out):
    import edge_tts
    import edge_tts.communicate as c
    c._SSL_CTX = _ssl_ctx()
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await com.save(out)


def _eleven(text, cfg, out):
    import urllib.request
    key = os.environ.get("ELEVENLABS_API_KEY") or cfg.get("key")
    if not key:
        raise SystemExit("ElevenLabs needs ELEVENLABS_API_KEY")
    vid = cfg["voice_id"]
    body = json.dumps({"text": text, "model_id": cfg.get("model", "eleven_multilingual_v2"),
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}", data=body,
                                 headers={"xi-api-key": key, "Content-Type": "application/json",
                                          "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, context=_ssl_ctx(), timeout=120) as r, open(out, "wb") as f:
        f.write(r.read())


def to_wav(src, dst, tempo=1.0):
    af = ["silenceremove=start_periods=1:start_threshold=-50dB",
          "areverse", "silenceremove=start_periods=1:start_threshold=-50dB", "areverse"]
    if abs(tempo - 1) > 1e-3:
        af.append(f"atempo={tempo}")
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", src, "-af", ",".join(af), "-ar", "44100", "-ac", "1",
                    "-sample_fmt", "s16", dst], check=True)


def read_wav(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a, w.getframerate()


def envelope(a, sr, fps=FPS):
    hop = sr // fps
    n = max(1, len(a) // hop)
    rms = np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, axis=1))
    return (rms / (rms.max() + 1e-6)).astype(np.float32)


def main():
    proj = os.path.abspath(sys.argv[1])
    force = "--force" in sys.argv
    story = load_json(os.path.join(proj, "story.json"))
    chan = load_json(os.path.join(os.getcwd(), "channel.json"), {}) or load_json(
        os.path.join(proj, "..", "..", "channel.json"), {}) or {}
    vcfg = {"engine": "edge", "voice": "hi-IN-MadhurNeural", "rate": "+6%", "pitch": "+0Hz"}
    vcfg.update(chan.get("voice", {}))
    vcfg.update(story.get("voice", {}))
    adir = os.path.join(proj, "audio")
    for sub in ("raw", "beats", "env"):
        os.makedirs(os.path.join(adir, sub), exist_ok=True)
    old = load_json(os.path.join(adir, "timing.json"), {}) or {}
    timing = {"voice": vcfg.get("voice") or vcfg.get("voice_id"), "beats": {}}
    total = 0.0
    words = 0
    for b in story["beats"]:
        bid, text = b["id"], b["text"].strip()
        words += len(text.split())
        h = hashlib.md5(json.dumps([text, vcfg, b.get("tempo", 1)], sort_keys=True).encode()).hexdigest()[:12]
        wav = os.path.join(adir, "beats", f"{bid}.wav")
        prev = old.get("beats", {}).get(bid, {})
        if force or prev.get("hash") != h or not os.path.exists(wav):
            eng = vcfg.get("engine", "edge")
            if eng == "own":
                src = None
                for ext in (".wav", ".mp3", ".m4a"):
                    p = os.path.join(adir, "own", bid + ext)
                    if os.path.exists(p):
                        src = p
                if not src:
                    raise SystemExit(f"missing own recording for {bid} (audio/own/{bid}.wav)")
            else:
                src = os.path.join(adir, "raw", f"{bid}.mp3")
                for attempt in range(4):
                    try:
                        if eng == "elevenlabs":
                            _eleven(text, vcfg, src)
                        else:
                            asyncio.run(_edge(text, vcfg["voice"], b.get("rate", vcfg.get("rate", "+0%")),
                                              vcfg.get("pitch", "+0Hz"), src))
                        break
                    except Exception as e:
                        if attempt == 3:
                            raise
                        print(f"  retry {bid}: {e}")
            to_wav(src, wav, float(b.get("tempo", 1.0)))
            print(f"  recorded {bid}")
        a, sr = read_wav(wav)
        env = envelope(a, sr)
        np.save(os.path.join(adir, "env", f"{bid}.npy"), env)
        dur = len(a) / sr
        pause = float(b.get("pause", story.get("pause", 0.32)))
        timing["beats"][bid] = {"hash": h, "voice": round(dur, 3), "dur": round(dur + pause + 0.12, 3)}
        total += dur + pause + 0.12
    timing["total"] = round(total, 2)
    save_json(os.path.join(adir, "timing.json"), timing)
    print(f"VOICE OK: {len(story['beats'])} beats, {total / 60:.2f} min, {words / (total / 60):.0f} words/min")


if __name__ == "__main__":
    main()
