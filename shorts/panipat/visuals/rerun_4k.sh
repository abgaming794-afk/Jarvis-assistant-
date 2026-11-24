#!/bin/bash
# re-render killed 4K chunks (fewer workers), wait for all, then concat + audio + 1080p copy
cd "$(dirname "$0")"
N=$(python3 -c "import panipat as p; print(int(p.END*60))" 2>/dev/null | tail -1); Q=$(( (N + 3) / 4 ))
for i in "$@"; do a=$((i*Q)); b=$(( (i+1)*Q < N ? (i+1)*Q : N ))
  python3 - "$a" "$b" "$i" <<'PY' 2>/dev/null &
import sys, subprocess, panipat as p
a, b, i = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "2160x3840", "-r", "60", "-i", "-",
                       "-c:v", "libx265", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1", "-x265-params", "log-level=error:pools=2",
                       f"../render/4k/part{i}.mp4"], stdin=subprocess.PIPE)
for f in range(a, b): ff.stdin.write(p.render(f / 60, 2160).tobytes())
ff.stdin.close(); ff.wait(); print("chunk", i, "ok", flush=True)
PY
done; wait
while pgrep -f "render_4k.sh" >/dev/null; do sleep 20; done
for i in 0 1 2 3; do n=$(ffprobe -v error -count_packets -select_streams v:0 -show_entries stream=nb_read_packets -of csv=p=0 ../render/4k/part$i.mp4); echo "part$i $n"; done
ffmpeg -y -loglevel error -f concat -safe 0 -i ../render/4k/list.txt -c copy ../render/4k/video.mp4
ffmpeg -y -loglevel error -i ../render/4k/video.mp4 -i ../audio/short_mix_norm.wav -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart ../Panipat_4K_master.mp4
ffprobe -v error -show_entries format=duration,size -of csv=p=0 ../Panipat_4K_master.mp4
echo "4K DONE $(date)"
