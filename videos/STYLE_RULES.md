# NAATYA house style — har video me LAAGU (koi point chhodna nahi)

Ye file Mughal Empire demo ke har feedback se bani hai. Naya video banane se pehle poori padho, aur render se pehle
neeche wali checklist tick karo. Engine: `videos/mughal-empire/studio/engine` (naye video me `studio/` copy karo).

## 1. Shuruaat ka kram (pipeline)
1. Topic: vidIQ se jo abhi trending hai (outliers dekh kar), user se confirm.
2. Research → `research/FACTS.md` (har number ke saath saal + source URL + safe Hindi wording; anumaan = "करीब / अनुमान के मुताबिक").
3. Script → script-doctor (hook, loops, FOMO, pacing) → fact-checker. Dialogue = "dramatised", asli quote nahi.
4. **Pehle character sheet + props sheet** banao, phir scenes.
5. **Pehle demo 360p (~3 min)**, user ki approval, phir poora video 360p "last demo", phir final **1440p 30 fps 10-bit**.
6. VO: user khud deta hai (apni recording) — recording sheet me har line ka ID, line ke baad 2 sec chup. (Backup: Gemini TTS, ElevenLabs.)
7. Har badlaav ke baad commit + push.

## 2. Scene aur pacing
- **Har scene 5–6 second se zyada nahi.** Lambi line ko todo (tools/splits.py). Har 3–5 sec me naya visual beat.
- **Jo narrator bole wahi screen par dikhe** — "haathi" bola to haathi, "tope" bola to tope chalti dikhe, "gaadiyon ki deewar" to araba. Visual hamesha narration samjhaye.
- Narration me jo jagah/saal aaye, map / timeline par woh dikhe.

## 3. Camera aur 3D
- **2D cartoon characters, 3D backgrounds** (code se bane set3d sets: court, palace, study, cell, tent, fort, village, battlefield, plain, cliff, river, map).
- **3D camera** — dolly, orbit, crane, push-in; kabhi static nahi.
- **Ek hi flow (one-shot)**: video jaise shuru ho, ek hi camera flow me khatam ho. Ek location ke beats ek continuous shot me (path keys, smootherstep glide), cut nahi.
- **Cards / documents / charts running scene ke upar** aate hain (peeche scene blur hokar chalta rahe), alag kaala screen nahi.
- **Characters jitter/kaanpne nahi chahiye** — subpixel compositing (`_paste_sub`) hamesha.

## 4. Transitions
- Seamless; cut ke pal poora frame dhaka ho.
- **Har baar cloud nahi.** Foreground 3D object wipes zyada: **khamba (pillar) — user ka favourite**, parda (curtain), jhanda (flag), haathi, fauj (army), darwaze (doors); kabhi-kabhi clouds/smoke/zoom/whip.
- Ek jaisa transition lagaatar do baar nahi.
- **Transition SFX nahi** (whoosh/swoosh band). Agar zaroori ho to max 10% volume.

## 5. Map
- **Map frame ke kinaron se bahar nahi dikhna chahiye** — bada global map (GV=(4,-22,136,66), GTW=4096), dark sea, koi edge/khali jagah nahi.
- Dark-mode map; highlighted ilaaka glowing **border ACCENT colour** me.
- Opening: **pehle map + saal (timeline)**, phir naam aate hi saltanat ka ilaaka fade-in/occupy hota dikhe.
- **Floating gol portrait medallion** (Nitish Rajput style) — raja ka asli portrait, crimson ring, neeche jagah ka pin, bagal me BEBAS naam + saal. Raja jahan se raaj karta tha wahan float kare.
- Pins: pulse rings + coordinates; routes animated.

## 6. Typography (sabse zaroori)
- **Sirf do fonts**: **Bebas Neue** (titles, numbers, 1–3 shabd CAPS) + **Poppins** (baaki sab, normal case).
- **Sab on-screen text Hinglish** (Roman script), Devanagari nahi.
- **Ek hi text colour**: TEXT = (247, 243, 234) ivory. Koi rangin text nahi.
- Highlight shabd = ACCENT underline (rang text ka nahi badalta).
- **Text kabhi character ke sir/chehre ke upar nahi** — labels_to_names + faces avoidance; text zones fixed:
  chapter top-left · timeline/caption/naam bottom-left · source + NAATYA tag top-right.
- Text style sab jagah consistent (same size scale, same card design).
- **Premium kinetic text animation** (`kinetic.py`): saal/number = **slot-machine roll** (e.g. 1500 → 1700 lock), titles = **letter rise** + tracking settle, phir light sweep + ACCENT rule. Saal kabhi seedha static nahi aata.
- Ginti/counter wale cards ka text bhi upar wale niyam maane.

## 7. Rang (colour theory)
- **ACCENT = Crimson (214, 58, 58)** — sab border, stroke, underline, rule, timeline marker, glow edge. **Yellow/gold border kabhi nahi.**
  (Navy map + gold ilaaka + ivory text ke saath crimson = Mughal laal; pins aur medallion ring ki hi family.)
- Badalna ho to sirf `studio/engine/palette.py` (ya env `NAATYA_ACCENT`).
- Background dark navy, text ivory, accent crimson — 60/30/10.

## 8. Saboot (documents)
- Asli public-domain document/photo/painting, 3D me, source credit top-right ("Srot"), `docs/credits.json` me credit.
- Painting ko "baad me bani painting" kahna, document nahi.

## 9. Audio
- Music mood "investigate"/mix; auto SFX band; transition SFX band (ya ≤10%).
- Story badle to `audio.py` dobara chalao (purana mix.wav purane whoosh rakh leta hai).
- VO: silence trim, andar ki chuppi ≤0.3 s; narrator atempo 1.1 (agar dheema ho).

## 10. Render
- Demo: `python3 studio/engine/render.py . --res 360 --workers 4 --fresh`
- Final: 1440p (2560×1440), 30 fps, 10-bit (yuv420p10le).

## Render se pehle checklist
- [ ] Koi scene > 6 s nahi
- [ ] Har line ka visual narration se match
- [ ] Map edge kahin nahi dikhta
- [ ] Text kisi sir/chehre par nahi; sirf Bebas + Poppins; sirf ivory text; sab Hinglish
- [ ] Saal/numbers kinetic roll; titles rise
- [ ] Border/stroke crimson, yellow nahi
- [ ] Transitions mix (khamba zyada), lagaatar repeat nahi, koi whoosh nahi
- [ ] One continuous camera flow; cards scene ke upar
- [ ] Characters jitter-free
- [ ] Medallions raja ki jagah par float
- [ ] Har fact FACTS.md me source ke saath
