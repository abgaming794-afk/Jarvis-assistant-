"""Generate audio/own/<id>.wav for every beat with Gemini TTS (key injected by the environment proxy).
usage: python3 tools/gemini_tts.py [--only s01,s02] [--force]"""
import base64, json, os, sys, time, urllib.request, urllib.error
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("TTS_MODEL", "gemini-3.8-flash-tts")
VOICE = {"N": "Charon", "BABUR": "Orus", "NANI": "Gacrux", "LODI": "Algenib", "SOLDIER": "Fenrir"}
STYLE = {"N": "deep, confident Hindi history documentary narrator, engaging brisk pace",
         "BABUR": "young Central Asian prince speaking Hindi", "NANI": "wise elderly grandmother speaking Hindi",
         "LODI": "arrogant sultan speaking Hindi", "SOLDIER": "nervous young soldier speaking Hindi"}
only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
force = "--force" in sys.argv
os.makedirs(P + "/audio/own", exist_ok=True)
beats = json.load(open(P + "/story.json", encoding="utf-8"))["beats"]
for b in beats:
    out = f"{P}/audio/own/{b['id']}.wav"
    if (only and b["id"] not in only) or (os.path.exists(out) and not force): continue
    sp = b.get("speaker", "N"); mood = b.get("tags", "").replace("[", "").replace("]", "").strip()
    direction = STYLE[sp] + (", " + mood if mood else "")
    body = {"contents": [{"parts": [{"text": f"[{direction}] {b['text']}"}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE[sp]}}}}}
    for attempt in range(6):
        try:
            req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                                         data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=180))
            raw = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            if raw[:4] != b"RIFF":  # raw PCM -> wrap as wav
                import wave
                with wave.open(out, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(raw)
            else:
                open(out, "wb").write(raw)
            print(b["id"], sp, VOICE[sp], f"{(len(raw) - 44) / 48000:.1f}s", flush=True); break
        except urllib.error.HTTPError as e:
            msg = e.read()[:200].decode(errors="ignore"); wait = 20 * (attempt + 1)
            print(b["id"], "HTTP", e.code, msg[:120], f"retry in {wait}s", flush=True)
            if e.code in (400, 403): sys.exit(1)
            time.sleep(wait)
        except Exception as e:
            print(b["id"], "ERR", e, flush=True); time.sleep(10)
    else:
        print(b["id"], "FAILED"); sys.exit(1)
    time.sleep(1)
print("DONE")
