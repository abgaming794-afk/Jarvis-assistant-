# Two-minute demo: 2D cartoon battles + 3D map (Khilafat VO 397.55-521.4 s)

Every war / event in the VO is shown as a 2D cartoon battle on a blurred photoreal battlefield (battle2d.py), the map
parts are 3D (tilted ground, orbit, extruded regions, standing pins, burning fronts - storyproof.py map3d), and each
event ends on its real proof (Wikipedia line, Mewar scroll). Scenes: satellite 3D -> Navsari proof -> 3D march ->
Navsari battle (Pulakeshin on the war elephant, arrow volley, clash, rout, "ARAB HAARE") -> 740 Saurashtra (Al-Hakam)
-> Chittor siege (ladders thrown back) -> Bappa Rawal chase + real scroll -> 743 / RAAZ #3 / Pratihara proof /
Blankinship -> Pratihara empire rising in 3D -> 851 Sulaiman: Pratihara cavalry + Wikipedia proof -> 3,000 soldiers
-> camera pulls out to the 3D world map, Umayyad Khilafat extruded -> fires on six fronts -> Day of Thirst, Khazar,
Defile (no winner), Tours, Akroinon, Berber revolt (27,000 Syrians) as cartoon battles -> the 3,000 diverted to Iraq
-> "Ghar mein aag, Sindh ki kaun sune?".

```bash
export KH_PROJ=/path/to/khilafat-india/ UTA_PLUGIN=/path/to/unexplored-truth-by-amrit
python3 demo120.py stills out 17 29 61 87.5                  # check frames
python3 demo120.py sfx                                       # sfx120.json (163 events)
python3 mix60.py sfx120.json mix120.wav                      # synthesised SFX + VO + music, -14 LUFS
# render in 4 parallel parts (frames = END*30 = 3769), concat, mux with mix120.wav
```
