"""Re-cut a batch with explicit cut times. usage: python3 tools/recut.py work/tts/<batch>.wav work/tts/<batch>.json t1 t2 ... (len(ids)-1 times)"""
import json, os, subprocess, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wav, ids = sys.argv[1], json.load(open(sys.argv[2])); cuts = [float(x) for x in sys.argv[3:]]
assert len(cuts) == len(ids) - 1, (len(cuts), len(ids))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav], capture_output=True, text=True).stdout)
cuts = [0.0] + cuts + [dur]
for i, b in enumerate(ids):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ss", f"{cuts[i]:.3f}", "-to", f"{cuts[i+1]:.3f}", "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse",
                    "-ar", "44100", "-ac", "1", f"{P}/audio/own/{b}.wav"], check=True)
    print(b, f"{cuts[i]:.2f}-{cuts[i+1]:.2f}")
