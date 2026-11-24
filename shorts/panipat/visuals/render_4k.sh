#!/bin/bash
# 4K master: 2160x3840, 60 fps, 10-bit HEVC, 4 parallel chunks (max 4 encoders), then concat + audio
cd "$(dirname "$0")"; mkdir -p ../render/4k
N=$(python3 -c "import panipat as p; print(int(p.END*60))" 2>/dev/null | tail -1); Q=$(( (N + 3) / 4 )); : > ../render/4k/list.txt
for i in 0 1 2 3; do a=$((i*Q)); b=$(( (i+1)*Q < N ? (i+1)*Q : N ))
  python3 - "$a" "$b" "$i" <<'PY' 2>/dev/null &
import sys, subprocess, panipat as p
a, b, i = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "2160x3840", "-r", "60", "-i", "-",
                       "-c:v", "libx265", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1", "-x265-params", "log-level=error",
                       f"../render/4k/part{i}.mp4"], stdin=subprocess.PIPE)
for f in range(a, b): ff.stdin.write(p.render(f / 60, 2160).tobytes())
ff.stdin.close(); ff.wait(); print("chunk", i, "ok", flush=True)
PY
  echo "file 'part$i.mp4'" >> ../render/4k/list.txt; done; wait
ffmpeg -y -loglevel error -f concat -safe 0 -i ../render/4k/list.txt -c copy ../render/4k/video.mp4
ffmpeg -y -loglevel error -i ../render/4k/video.mp4 -i ../audio/short_mix_norm.wav -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart ../Panipat_4K_master.mp4
ffmpeg -y -loglevel error -i ../Panipat_4K_master.mp4 -vf scale=1080:1920 -c:v libx264 -preset medium -crf 20 -c:a copy ../render/Panipat_1080p.mp4
echo "4K DONE $(date)"
