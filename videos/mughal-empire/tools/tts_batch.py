"""Gemini TTS in batches (free tier = ~10 requests/day/model). Narrator lines go 12 per request and are cut
with tts_align.py; dialogue lines are one request each on a second model.
usage: python3 tools/tts_batch.py"""
import base64, json, os, subprocess, sys, time, urllib.request, urllib.error, wave
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NARR_MODEL, DLG_MODEL = "gemini-3.1-flash-tts-preview", "gemini-2.5-pro-preview-tts"
VOICE = {"N": "Charon", "BABUR": "Orus", "NANI": "Gacrux", "LODI": "Algenib", "SOLDIER": "Fenrir"}
STYLE = {"BABUR": "young Central Asian prince speaking Hindi", "NANI": "wise elderly grandmother speaking Hindi",
         "LODI": "arrogant sultan speaking Hindi", "SOLDIER": "nervous young soldier speaking Hindi"}
beats = json.load(open(P + "/story.json", encoding="utf-8"))["beats"]
done = lambda b: os.path.exists(f"{P}/audio/own/{b['id']}.wav")

def tts(model, voice, text, out):
    body = {"contents": [{"parts": [{"text": text}]}], "generationConfig": {"responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for attempt in range(3):
        try:
            r = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                       data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            raw = base64.b64decode(json.load(urllib.request.urlopen(r, timeout=300))["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            if raw[:4] == b"RIFF": open(out, "wb").write(raw)
            else:
                with wave.open(out, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(raw)
            return True
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")
            print("HTTP", e.code, model, msg[:160].replace("\n", " "), flush=True)
            if e.code == 429 and "PerDay" in msg: return False
            time.sleep(30 * (attempt + 1))
    return False

os.makedirs(P + "/work/tts", exist_ok=True)
narr = [b for b in beats if b["speaker"] == "N" and not done(b)]
for k in range(0, len(narr), 12):
    chunk = narr[k:k + 12]; tag = f"n_{chunk[0]['id']}"
    text = ("[deep, confident Hindi history documentary narrator, engaging pace. Read each numbered line, then stay "
            "completely silent for two full seconds before the next line. Do not read the numbers.]\n" +
            "\n".join(f"{i+1}. {b['text']}" for i, b in enumerate(chunk)))
    json.dump([b["id"] for b in chunk], open(f"{P}/work/tts/{tag}.json", "w"))
    if not tts(NARR_MODEL, "Charon", text, f"{P}/work/tts/{tag}.wav"): sys.exit("narrator quota exhausted")
    print("batch", tag, len(chunk), "lines", flush=True)
    subprocess.run([sys.executable, P + "/tools/tts_align.py", f"{P}/work/tts/{tag}.wav", f"{P}/work/tts/{tag}.json"], check=True)
for b in beats:
    if b["speaker"] == "N" or done(b): continue
    mood = b.get("tags", "").replace("[", "").replace("]", "").strip()
    raw = f"{P}/work/tts/{b['id']}_raw.wav"
    if not tts(DLG_MODEL, VOICE[b["speaker"]], f"[{STYLE[b['speaker']]}, {mood}] {b['text']}", raw): sys.exit("dialogue quota exhausted")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse",
                    "-ar", "44100", "-ac", "1", f"{P}/audio/own/{b['id']}.wav"], check=True)
    print("dialogue", b["id"], b["speaker"], VOICE[b["speaker"]], flush=True)
print("ALL DONE")
