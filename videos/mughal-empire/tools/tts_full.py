"""Whole-video VO with Gemini TTS (free tier ~10 requests/day/model): narrator lines in big batches (one request
~40 lines), dialogue one request per character; each batch is cut into audio/own/<id>.wav by an offline DP aligner
(cuts chosen among silences so each line's length matches its text). Resumable: lines with a wav are skipped.
usage: python3 tools/tts_full.py [--only-narr|--only-dlg] [--max N]"""
import base64, hashlib, json, os, re, subprocess, sys, time, urllib.request, urllib.error, wave
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NARR_MODELS = os.environ.get("NARR_MODELS", "gemini-2.5-flash-preview-tts,gemini-2.5-pro-preview-tts").split(",")
DLG_MODELS = ["gemini-2.5-pro-preview-tts", "gemini-2.5-flash-preview-tts"]
VOICE = {"N": "Charon", "BABUR": "Orus", "NANI": "Gacrux", "LODI": "Algenib", "SOLDIER": "Fenrir", "HUMAYUN": "Iapetus",
         "BAIRAM": "Alnilam", "ROE": "Puck", "DARA": "Enceladus", "AURANGZEB": "Schedar", "NADIR": "Algenib",
         "CROWD": "Sadaltager", "SEPOY": "Achird"}
STYLE = {"BABUR": "proud Central Asian king, firm and brave", "SOLDIER": "nervous soldier", "HUMAYUN": "gentle emotional king blessing his newborn son",
         "BAIRAM": "stern battle-hardened regent", "ROE": "polite English ambassador with a slight English accent",
         "DARA": "angry proud prince", "AURANGZEB": "cold, calm, calculating prince/emperor", "NADIR": "awestruck Persian conqueror",
         "CROWD": "panicked shouting voice from a crowd", "SEPOY": "rebel soldier shouting with hope"}
NARR_STYLE = ("[deep, rich, confident Hindi history documentary narrator; cinematic, engaging, measured pace; dramatic "
              "where the text is dramatic. Read each numbered line, then stay completely silent for two full seconds "
              "before the next line. Do not read the numbers.]")
BATCH = int(os.environ.get("BATCH", 40))
OWN = P + "/audio/own"; WK = P + "/work/tts_full"
os.makedirs(OWN, exist_ok=True); os.makedirs(WK, exist_ok=True)
REDO = None   # set below: every demo line is re-voiced so the whole film has one narrator model

def lines():
    out = []
    for ln in open(P + "/SCRIPT.md", encoding="utf-8"):
        m = re.match(r"- (s\d\db?) ((?:\[[^\]]*\])+) (.*)", ln.strip())
        if m:
            out.append(dict(id=m.group(1), who="DLG" if "DIALOGUE" in m.group(2) else "N", text=m.group(3).strip()))
    out += json.load(open(P + "/script_full/lines.json", encoding="utf-8"))
    return out
L = lines(); T = {x["id"]: x["text"] for x in L}
REDO = {x["id"] for x in L if re.match(r"s\d\db?$", x["id"])}
stamp_f = WK + "/stamps.json"; stamps = json.load(open(stamp_f)) if os.path.exists(stamp_f) else {}
h = lambda t: hashlib.md5(t.encode()).hexdigest()[:10]
def done(x):
    if not os.path.exists(f"{OWN}/{x['id']}.wav"): return False
    if x["id"] in REDO and stamps.get(x["id"]) != h(x["text"]): return False
    return x["id"] not in stamps or stamps[x["id"]] == h(x["text"])

def tts(models, voice, text, out):
    body = {"contents": [{"parts": [{"text": text}]}], "generationConfig": {"responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for model in models:
        for attempt in range(3):
            try:
                r = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                           data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
                resp = json.load(urllib.request.urlopen(r, timeout=600))
                c = resp.get("candidates", [{}])[0]
                if "content" not in c:
                    print("NO AUDIO", model, c.get("finishReason"), json.dumps(resp.get("promptFeedback", {}))[:200], flush=True)
                    if c.get("finishReason") in ("SAFETY", "PROHIBITED_CONTENT", "OTHER"):
                        return "SAFETY"
                    time.sleep(5); continue
                raw = base64.b64decode(c["content"]["parts"][0]["inlineData"]["data"])
                if raw[:4] == b"RIFF": open(out, "wb").write(raw)
                else:
                    with wave.open(out, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(raw)
                return model
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="ignore")
                print("HTTP", e.code, model, msg[:200].replace("\n", " "), flush=True)
                if e.code == 429 and "PerDay" in msg: break
                time.sleep(40 * (attempt + 1))
            except Exception as e:
                print("ERR", model, e, flush=True); time.sleep(20)
    return None

def dur_of(f):
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
    except ValueError:
        return 0.0

def dp_cut(wav, ids):
    dur = dur_of(wav)
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", "silencedetect=n=-34dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    sil = list(zip(map(float, re.findall(r"silence_start: ([\d.]+)", log)), map(float, re.findall(r"silence_end: ([\d.]+)", log))))
    lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    cand = [((a + b) / 2, b - a) for a, b in sil if a > 0.05 and b < dur - 0.05]
    wf = lambda t: len(re.sub(r"[\s.,…—?!-]", "", t)) + 3 * len(re.findall(r"[.,…—?!]", t))
    W = [wf(T[i]) for i in ids]; rate = (dur - lead) / sum(W); n, m = len(ids), len(cand)
    if n == 1: return [0.0, dur]
    if len(cand) < n - 1:
        acc, out = lead, [0.0]
        for k in range(n - 1):
            acc += W[k] * rate; out.append(acc)
        return out + [dur]
    INF = 1e18; cost = lambda t0, t1, k: ((t1 - t0 - W[k] * rate) / (W[k] * rate)) ** 2
    dp = [[INF] * m for _ in range(n)]; bk = [[-1] * m for _ in range(n)]
    for j in range(m): dp[0][j] = cost(lead, cand[j][0], 0) - 0.6 * min(cand[j][1], 1.5)
    for k in range(1, n - 1):
        for j in range(m):
            best, bi = INF, -1
            for i in range(j):
                if dp[k - 1][i] < INF:
                    c = dp[k - 1][i] + cost(cand[i][0], cand[j][0], k)
                    if c < best: best, bi = c, i
            if bi >= 0: dp[k][j], bk[k][j] = best - 0.6 * min(cand[j][1], 1.5), bi
    best, bj = INF, -1
    for j in range(m):
        if dp[n - 2][j] < INF:
            c = dp[n - 2][j] + cost(cand[j][0], dur, n - 1)
            if c < best: best, bj = c, j
    if bj < 0:
        acc, out = lead, [0.0]
        for k in range(n - 1):
            acc += W[k] * rate; out.append(acc)
        return out + [dur]
    cuts, k, j = [], n - 2, bj
    while k >= 0: cuts.append(cand[j][0]); j = bk[k][j]; k -= 1
    return [0.0] + cuts[::-1] + [dur]

def cut(wav, ids):
    e = dp_cut(wav, ids)
    for i, b in enumerate(ids):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ss", f"{e[i]:.3f}", "-to", f"{e[i+1]:.3f}", "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse",
                        "-ar", "44100", "-ac", "1", f"{OWN}/{b}.wav"], check=True)
        stamps[b] = h(T[b])
        d = dur_of(f"{OWN}/{b}.wav"); w = len(T[b].split())
        flag = "  <-- CHECK" if not (w / 4.8 < d < w / 1.3 + 0.9) else ""
        print(f"  {b:5s} {d:4.1f}s {w:2d}w{flag}", flush=True)
    json.dump(stamps, open(stamp_f, "w"), indent=0)

maxreq = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 99
nreq = 0
if "--only-dlg" not in sys.argv:
    todo = [x for x in L if x["who"] == "N" and not done(x)]
    print(len(todo), "narrator lines to make", flush=True)
    def run(chunk):
        global nreq
        if nreq >= maxreq: return
        tag = f"n_{chunk[0]['id']}_{len(chunk)}"; ids = [x["id"] for x in chunk]
        text = NARR_STYLE + "\n" + "\n".join(f"{i+1}. {x['text']}" for i, x in enumerate(chunk))
        m = tts(NARR_MODELS, VOICE["N"], text, f"{WK}/{tag}.wav"); nreq += 1
        if m == "SAFETY":
            if len(chunk) == 1:
                print("  BLOCKED line", chunk[0]["id"], chunk[0]["text"], flush=True); return
            h2 = len(chunk) // 2; run(chunk[:h2]); run(chunk[h2:]); return
        if not m: sys.exit("narrator quota exhausted for today")
        got = dur_of(f"{WK}/{tag}.wav"); exp = sum(len(x["text"].split()) for x in chunk) / 2.6 + 1.2 * len(chunk)
        print("batch", tag, len(chunk), "lines", f"{got:.0f}s (exp ~{exp:.0f}s)", m, flush=True)
        if got < 0.55 * exp or got > 1.7 * exp:
            print("  BAD LENGTH audio -> splitting batch", flush=True)
            if len(chunk) == 1: return
            h2 = len(chunk) // 2; run(chunk[:h2]); run(chunk[h2:]); return
        json.dump(ids, open(f"{WK}/{tag}.json", "w")); cut(f"{WK}/{tag}.wav", ids)
    for k in range(0, len(todo), BATCH):
        if nreq >= maxreq: break
        run(todo[k:k + BATCH])
if "--only-narr" not in sys.argv:
    by = {}
    for x in L:
        if x["who"] not in ("N", "DLG") and not done(x): by.setdefault(x["who"], []).append(x)
    for who, xs in by.items():
        if nreq >= maxreq: break
        tag = f"d_{who}"; ids = [x["id"] for x in xs]
        text = (f"[{STYLE.get(who, '')}, speaking Hindi. Read each numbered line as a separate short speech, then stay silent "
                f"for two seconds. Do not read the numbers.]\n" + "\n".join(f"{i+1}. {x['text']}" for i, x in enumerate(xs)))
        m = tts(DLG_MODELS, VOICE.get(who, "Fenrir"), text, f"{WK}/{tag}.wav"); nreq += 1
        if m == "SAFETY": print("  BLOCKED dialogue", who, flush=True); continue
        if not m: sys.exit("dialogue quota exhausted for today")
        print("dialogue", who, len(xs), m, flush=True); cut(f"{WK}/{tag}.wav", ids)
print("DONE", sum(1 for x in L if x["who"] != "DLG" and done(x)), "/", sum(1 for x in L if x["who"] != "DLG"))
