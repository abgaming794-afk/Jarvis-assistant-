# One-minute story-then-proof demo on a real VO (Khilafat, Navsari section)

Made with the user's own Khilafat voice-over (VO 397.55-456.4 s), code-made SFX and a soft music bed.
Beats: satellite + Navsari pin -> "sabse pakka saboot" = real Wikipedia line -> parchment march Sindh-Kutch-Saurashtra
-> animated story (photoreal AI battle + the channel's own 2D king and 2D men, "ARAB HAARE" stamp, fireworks) ->
740 Al-Hakam (AI card, labelled) -> Chittor siege failed -> Bappa Rawal real Mewar scroll -> 2D man thinks ->
743 banner peels off -> RAAZ #3 -> pennants + angry map mascots -> Pratihara Wikipedia proof -> Blankinship card.

```bash
export KH_PROJ=/path/to/khilafat-india/ UTA_PLUGIN=/path/to/goeglobetales-copy-edt-style-long-and-short-form
python3 demo60.py stills out 1.5 12 20 30        # check frames
python3 demo60.py sfx                             # writes sfx60.json (61 events timed to VO words)
python3 mix60.py                                  # synthesises SFX (sfx/*.wav), VO slice + music -> mix60.wav (-14 LUFS)
for i in 0 1 2 3; do python3 demo60.py video part$i.mp4 640 30 $((i*455)) $(((i+1)*455+ (i==3)*50)) & done; wait
printf "file 'part0.mp4'\nfile 'part1.mp4'\nfile 'part2.mp4'\nfile 'part3.mp4'\n" > parts.txt
ffmpeg -f concat -safe 0 -i parts.txt -i mix60.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -t 60.65 DEMO60.mp4
```

SFX library in `mix60.py` (all synthesised, no samples): whoosh, swish, pop, pin, chime, tick (timeline ratchet),
paper rustle, stamp, marker squeak, march drum, big drum (title hit), boom (iris), riser, firework (whistle + bang +
crackle), battle ambience (rumble, crowd roar, sword clangs, war drums). SFX sit 6 dB under their listed gain
(channel rule: half loudness under the VO); music bed at -25 dB.
