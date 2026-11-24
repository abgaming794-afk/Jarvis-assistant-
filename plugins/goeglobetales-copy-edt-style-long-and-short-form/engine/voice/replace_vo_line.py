"""Replace one spoken line inside the full voice-over without re-recording everything.

Usage:
  python3 replace_vo_line.py VO_IN NEW_LINE OUT_WAV OLD_START OLD_END PREV_END NEXT_START [--gap 0.30] [--pause 0.15] [--max-tempo 1.08]

  VO_IN       full voice-over (mp3/wav)
  NEW_LINE    the re-recorded line (mp3/wav), same voice + settings
  OLD_START/OLD_END  speech span of the wrong line in VO time (from full_units.json)
  PREV_END / NEXT_START  end of the previous line / start of the next line (pauses around the slot)

What it does (the method that worked on 'Naya Axis' u117):
  1. Finds speech segments in NEW_LINE (silencedetect -45 dB), drops leading/trailing silence.
  2. Caps every internal pause to --pause seconds (natural but tight).
  3. Fits the result into [PREV_END+gap, NEXT_START-gap] with atempo (refuses above --max-tempo;
     then shorten the script line or re-time the visuals instead).
  4. Matches loudness (RMS of voiced samples) to the old line, silences the old slot, writes OUT_WAV (48 kHz mono 16-bit).
  5. Prints new start/end and the start time of each phrase, to update full_units.json (text, start, end, anchors)
     so captions and keyword-synced visuals follow the new words.
After this: re-run mix_full.py (point it at OUT_WAV), regenerate SFX (full.py sfx), and re-render ONLY the chunk(s)
that contain the line (render_full.py skips chunks that have a .done file; delete that chunk's .done).
"""
import argparse, re, subprocess
import numpy as np, wave

SR = 48000
ap = argparse.ArgumentParser()
for a in ("vo_in", "new_line", "out_wav"): ap.add_argument(a)
for a in ("old_start", "old_end", "prev_end", "next_start"): ap.add_argument(a, type=float)
ap.add_argument("--gap", type=float, default=0.30); ap.add_argument("--pause", type=float, default=0.15)
ap.add_argument("--max-tempo", type=float, default=1.08)
A = ap.parse_args()

def load(p):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

vo, new = load(A.vo_in), load(A.new_line)
log = subprocess.run(["ffmpeg", "-i", A.new_line, "-af", "silencedetect=n=-45dB:d=0.08", "-f", "null", "-"], capture_output=True, text=True).stderr
ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
dur = len(new) / SR
edges = sorted(zip(ss, se + [dur] * (len(ss) - len(se))))
segs, cur = [], 0.0
for a, b in edges:
    if a - cur > 0.05: segs.append((max(0, cur - 0.01), a + 0.01))
    cur = b
if dur - cur > 0.05: segs.append((cur - 0.01, dur))
fade = int(0.012 * SR); parts, starts, acc = [], [], 0.0
for k, (a, b) in enumerate(segs):
    s = new[int(a * SR):int(b * SR)].copy(); s[:fade] *= np.linspace(0, 1, fade); s[-fade:] *= np.linspace(1, 0, fade)
    starts.append(acc); parts.append(s); acc += len(s) / SR
    if k < len(segs) - 1: parts.append(np.zeros(int(A.pause * SR), np.float32)); acc += A.pause
cat = np.concatenate(parts)
t0, t1 = A.prev_end + A.gap, A.next_start - A.gap
tempo = max(1.0, len(cat) / SR / (t1 - t0))
if tempo > A.max_tempo: raise SystemExit(f"needs atempo {tempo:.3f} > {A.max_tempo}: shorten the line or shift the next visuals")
fit = cat
if tempo > 1.0001:
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={tempo:.5f}", "-f", "f32le", "-"],
                         input=cat.tobytes(), capture_output=True, check=True).stdout
    fit = np.frombuffer(out, np.float32).copy()
def rms(x): x = x[np.abs(x) > 0.01]; return float(np.sqrt(np.mean(x ** 2))) if len(x) else 1.0
fit *= rms(vo[int(A.old_start * SR):int(A.old_end * SR)]) / rms(fit)
res = vo.copy(); res[int(A.prev_end * SR):int(A.next_start * SR)] = 0
i0 = int(t0 * SR); res[i0:i0 + len(fit)] = fit[:len(res) - i0]
with wave.open(A.out_wav, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(res, -1, 1) * 32767).astype(np.int16).tobytes())
print(f"tempo {tempo:.3f}  new start {t0:.3f}  new end {t0 + len(fit) / SR:.3f}")
print("phrase starts (VO time):", [round(t0 + s / tempo, 3) for s in starts])
