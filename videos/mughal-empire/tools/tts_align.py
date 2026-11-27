"""Cut a batch recording into per-beat wavs: Gemini estimates line boundaries, cuts snap to the nearest silence.
usage: python3 tools/tts_align.py work/tts/batchN.wav work/tts/batchN.json"""
import base64, json, os, re, subprocess, sys, time, urllib.request, urllib.error
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wav, idsf = sys.argv[1], sys.argv[2]
ids = json.load(open(idsf)); beats = {b["id"]: b for b in json.load(open(P + "/story.json", encoding="utf-8"))["beats"]}
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav], capture_output=True, text=True).stdout)
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", "silencedetect=n=-38dB:d=0.3", "-f", "null", "-"], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
sil = list(zip(st, en))
lines = "\n".join(f"{i+1}. {beats[b]['text']}" for i, b in enumerate(ids))
prompt = (f"This Hindi narration audio ({dur:.1f} s) reads these {len(ids)} lines in order:\n{lines}\n\n"
          "For every line give the time in seconds where it starts and ends in the audio. "
          'Answer only JSON: [{"n":1,"start":0.0,"end":0.0}, ...]')
body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(open(wav, "rb").read()).decode()}},
                                {"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
for m in ["gemini-3.5-flash", "gemini-3.7-flash", "gemini-3-flash-preview", "gemini-3.8-flash", "gemini-3.1-flash-lite"]:
    try:
        r = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        est = json.loads(json.load(urllib.request.urlopen(r, timeout=180))["candidates"][0]["content"]["parts"][0]["text"]); break
    except urllib.error.HTTPError as e:
        print(m, e.code); time.sleep(2)
else:
    sys.exit("no aligner model available")
est = sorted(est, key=lambda x: x["n"])
# boundary k (between line k and k+1): midpoint of est end_k/start_k+1, snapped to the nearest silence midpoint
cuts = [0.0]
for k in range(len(ids) - 1):
    t = (est[k]["end"] + est[k + 1]["start"]) / 2
    best = min(sil, key=lambda s: abs((s[0] + s[1]) / 2 - t)) if sil else (t, t)
    c = (best[0] + best[1]) / 2 if abs((best[0] + best[1]) / 2 - t) < 1.2 else t
    cuts.append(max(c, cuts[-1] + 0.5))
cuts.append(dur)
os.makedirs(P + "/audio/own", exist_ok=True)
for i, b in enumerate(ids):
    a, z = cuts[i], cuts[i + 1]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ss", f"{a:.3f}", "-to", f"{z:.3f}",
                    "-af", "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse",
                    "-ar", "44100", "-ac", "1", f"{P}/audio/own/{b}.wav"], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{P}/audio/own/{b}.wav"], capture_output=True, text=True).stdout)
    w = len(beats[b]["text"].split())
    flag = "  <-- CHECK" if not (w / 4.5 < d < w / 1.4 + 0.8) else ""
    print(f"{b:5s} {a:6.2f}-{z:6.2f} {d:4.1f}s {w:2d}w{flag}")
