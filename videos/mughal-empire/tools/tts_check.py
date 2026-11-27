"""Transcribe several audio/own/<id>.wav clips in one request and compare with the script."""
import base64, json, os, sys, urllib.request, urllib.error, time
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = json.load(open(sys.argv[1])) if sys.argv[1].endswith(".json") else sys.argv[1].split(",")
beats = {b["id"]: b for b in json.load(open(P + "/story.json", encoding="utf-8"))["beats"]}
parts = []
for i, b in enumerate(ids):
    parts += [{"text": f"Clip {i+1}:"}, {"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(open(f"{P}/audio/own/{b}.wav", "rb").read()).decode()}}]
parts.append({"text": f'Transcribe each of the {len(ids)} Hindi clips separately, in Devanagari. Answer only JSON: ["clip 1 text", ...]'})
body = {"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0}}
for m in ["gemini-3.5-flash", "gemini-3.7-flash", "gemini-3-flash-preview", "gemini-3.8-flash", "gemini-3.1-flash-lite"]:
    try:
        r = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        out = json.loads(json.load(urllib.request.urlopen(r, timeout=180))["candidates"][0]["content"]["parts"][0]["text"]); break
    except urllib.error.HTTPError as e:
        print(m, e.code); time.sleep(2)
for b, t in zip(ids, out):
    print(f"{b:5s} HEARD: {t}\n      SCRIPT: {beats[b]['text']}")
