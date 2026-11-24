#!/bin/bash
# usage: render_chunks.sh WIDTH FPS OUT.mp4   (4 parallel chunks, then concat)
cd "$(dirname "$0")"; W=$1; FPS=$2; OUT=$3; mkdir -p ../render
N=$(python3 -c "import panipat as p; print(int(p.END*$FPS))" 2>/dev/null | tail -1)
Q=$(( (N + 3) / 4 )); : > ../render/list.txt
for i in 0 1 2 3; do a=$((i*Q)); b=$(( (i+1)*Q < N ? (i+1)*Q : N )); python3 panipat.py video ../render/part$i.mp4 $W $FPS $a $b 2>/dev/null & echo "file 'part$i.mp4'" >> ../render/list.txt; done; wait
ffmpeg -y -loglevel error -f concat -safe 0 -i ../render/list.txt -c copy "$OUT"; echo "done $OUT $N frames"
