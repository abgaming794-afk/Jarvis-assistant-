"""Split ONE full voice-over recording into per-beat files.
python split_vo.py <project> <vo.mp3|wav> [--noise -35] [--min 0.18] [--cuts 6.5,12.5,...]

Use it when the voice comes as a single file (ElevenLabs export, your own recording, a file uploaded to Gemini/any
agent). It detects pauses with ffmpeg `silencedetect`, then picks the N-1 pauses that best match where each beat
should end (by the beat's share of the script's characters), keeping the order. Writes audio/own/<id>.wav for every
beat — voice.py then uses them automatically. Read the printed table: any beat whose length is far from its
expected length means a line was skipped or added in the recording. If the guess is wrong, listen (or transcribe
with timestamps) and pass the exact start time of beats 2..N with --cuts. Also writes audio/own/_cuts.txt.
"""
import os, re, subprocess, sys
import numpy as np
from common import load_json, ffmpeg_bin
from voice import read_wav

SR = 44100
W_LEN, W_DUR, W_SENT, SIG = 3.0, 0.5, 0.5, 0.25  # tuned on 10 test VOs (0 wrong cuts): length fit, long-pause pref, sentences


def silences(wav, noise, mind):
    out = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", wav, "-af", f"silencedetect=n={noise}dB:d={mind}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(st, en))


def best_cuts(cands, durs, s0, s1, w, sents=None):
    """Choose len(w)-1 pauses (in order) so every segment length matches its share of the script, preferring long
    pauses (between lines people pause longer than at a comma). Segment DP, O(n*m^2)."""
    n, m = len(w), len(cands)
    if m < n - 1:
        return None
    # compare SPOKEN time (segment minus its pauses) with the beat's share of the script's characters
    exp = ((s1 - s0) - sum(durs)) * w / w.sum()
    pts = [s0] + list(cands) + [s1]
    half = [0.0] + [d / 2 for d in durs] + [0.0]
    csil = np.cumsum([0.0] + list(durs) + [0.0])   # csil[q] = total pause before point q
    sents = sents if sents is not None else [1] * n
    # the K longest pauses are the sentence pauses (K = sentence boundaries in the script); beats end only on them
    K = min(m, sum(sents) - 1)
    big = sorted(durs, reverse=True)[K - 1] if K > 0 else 9e9
    isbig = [1 if d >= big else 0 for d in durs]
    bonus = [0.0] + [min(d, 2.0) for d in durs] + [0.0]
    longp = np.cumsum([0] + isbig + [0])
    INF = float("inf")
    M = m + 2
    cost = np.full((n + 1, M), INF)
    back = np.zeros((n + 1, M), int)
    cost[0, 0] = 0.0
    for i in range(1, n + 1):
        lo, hi = i, M - (n - i)
        for k in (range(M - 1, M) if i == n else range(lo, hi)):
            best, arg = INF, -1
            for j in range(i - 1, k):
                c = cost[i - 1, j]
                if c == INF:
                    continue
                L = pts[k] - pts[j] - (csil[k - 1] - csil[j] if k - 1 >= j else 0) - half[j] - half[k]
                inside = longp[k - 1] - longp[j] if k - 1 >= j else 0  # long pauses strictly inside the segment
                c += W_LEN * ((L - exp[i - 1]) / (SIG * exp[i - 1] + 0.6)) ** 2 - W_DUR * bonus[k]
                c += W_SENT * abs(inside - (sents[i - 1] - 1))
                if c < best:
                    best, arg = c, j
            cost[i, k], back[i, k] = best, arg
    k, out = M - 1, []
    for i in range(n, 0, -1):
        k = back[i, k]
        out.append(k)
    return [pts[k] for k in reversed(out)][1:]


def main():
    proj, src = os.path.abspath(sys.argv[1]), sys.argv[2]
    noise = float(sys.argv[sys.argv.index("--noise") + 1]) if "--noise" in sys.argv else -35
    mind = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 0.18
    story = load_json(os.path.join(proj, "story.json"))
    beats = story["beats"]
    own = os.path.join(proj, "audio", "own")
    os.makedirs(own, exist_ok=True)
    full = os.path.join(own, "_full.wav")
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", src, "-ar", str(SR), "-ac", "1", full], check=True)
    a, _ = read_wav(full)
    total = len(a) / SR
    sil = silences(full, noise, mind)
    # speech span (ignore leading / trailing silence)
    s0 = sil[0][1] if sil and sil[0][0] <= 0.05 else 0.0
    s1 = sil[-1][0] if sil and sil[-1][1] >= total - 0.05 else total
    inner = [(x, y) for x, y in sil if s0 < (x + y) / 2 < s1]
    w = np.array([max(1, len(re.sub(r"\s+", "", b["text"]))) for b in beats], float)
    sents = [max(1, len([q for q in re.split(r"(?:[.!?\u0964\u2026]|\.\.\.)+", b["text"]) if q.strip()])) for b in beats]
    if "--cuts" in sys.argv:       # exact beat start times (s) for beats 2..N, e.g. from listening / a transcript
        cuts = [float(x) for x in sys.argv[sys.argv.index("--cuts") + 1].split(",")]
        if len(cuts) != len(beats) - 1:
            raise SystemExit(f"--cuts needs {len(beats) - 1} times, got {len(cuts)}")
    else:
        cuts = best_cuts([(x + y) / 2 for x, y in inner], [y - x for x, y in inner], s0, s1, w, sents) if len(beats) > 1 else []
    if cuts is None:
        for n2, d2 in ((noise + 5, mind * .7), (noise + 10, .1)):
            sil2 = [(x, y) for x, y in silences(full, n2, d2) if s0 < (x + y) / 2 < s1]
            cuts = best_cuts([(x + y) / 2 for x, y in sil2], [y - x for x, y in sil2], s0, s1, w, sents)
            if cuts:
                print(f"note: used looser silence detection ({n2} dB, {d2:.2f} s)")
                break
    if cuts is None:
        print("WARNING: not enough pauses in the recording; cutting by script proportion (check every beat!)")
        cuts = list(s0 + (s1 - s0) * np.cumsum(w)[:-1] / w.sum())
    edges = [s0] + cuts + [s1]
    print(f"{'beat':6} {'spoken':>6} {'expected':>9}")
    for i, b in enumerate(beats):
        t0, t1 = max(0, edges[i] - 0.05), min(total, edges[i + 1] + 0.05)
        seg = a[int(t0 * SR):int(t1 * SR)]
        out = os.path.join(own, f"{b['id']}.wav")
        import wave
        with wave.open(out, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(SR)
            f.writeframes((np.clip(seg, -1, 1) * 32767).astype(np.int16).tobytes())
        spoken = (edges[i + 1] - edges[i]) - sum(min(y, edges[i + 1]) - max(x, edges[i]) for x, y in inner
                                                  if x < edges[i + 1] and y > edges[i])
        exp = ((s1 - s0) - sum(y - x for x, y in inner)) * w[i] / w.sum()
        flag = "  <-- check" if abs(spoken - exp) > max(1.0, exp * .4) else ""
        print(f"{b['id']:6} {spoken:6.2f} {exp:9.2f}{flag}")
    open(os.path.join(own, "_cuts.txt"), "w").write(",".join(f"{c:.2f}" for c in cuts) + "\n")
    os.remove(full)
    print(f"SPLIT OK: {len(beats)} files in {own}. Next: python voice.py {proj}")


if __name__ == "__main__":
    main()
