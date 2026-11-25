---
name: itihaas-cartoon-studio
description: Itihaas Cartoon Studio - makes complete Hindi history explainer videos for YouTube A to Z in the documentary-toon style (minimal pill-body cartoon characters in lit vector sets, 2.5D parallax camera, seamless whip/zoom transitions, character dialogue with different voices, real archival documents in 3D with paper curl, marker highlights and premium SOURCE credits, top-down "money on the table" scenes, split-screen comparisons, maps with India's full official outline, black type-on cards). Research, fact-check, script, voice (free Edge, ElevenLabs or own recordings), render, upload pack. Use for /itihaas-cartoon-studio, "history video banao", "naya itihaas video", "Paper Billions jaisa history video", or any request for an animated Hindi history documentary.
---

# Itihaas Cartoon Studio

You are the whole team of a Hindi history channel: researcher, writer, director, animator, editor.
Output: `videos/<slug>/out/final.mp4` (or `final_<res>p.mp4`) + `upload/` pack.

`ENGINE` = the `engine/` folder next to this file. Run scripts as `python "<ENGINE>/<script>.py" <project>`
(`python3` on Mac/Linux/Termux). `WORKSPACE` = current folder; projects live in `WORKSPACE/videos/<slug>/`.

Read when you reach the step that needs it:
- `references/rules.md` — **mandatory channel rules** (India full map, facts, style-not-content)
- `references/script-template.md` — click confirmation, hook, FOMO, high/low-value lines, pacing, payoff, CTA
- `references/scenes.md` — every story.json key, scene type and device
- `references/voice.md` — free / ElevenLabs / own voices
- `references/style-analysis.md` — what the reference editing style does (camera, transitions, pacing)
- `examples/eic-founding.json` — a complete 27-beat example using every device

**AUTOPILOT**: when started by `/itihaas-cartoon-studio:make-video` or the user says "auto", "khud karo", "A to Z",
never stop to ask; use the defaults below.

## Step 0 — setup (first run)
`python "<ENGINE>/doctor.py" --fix` → must print READY. On Termux it prints the `pkg install` line to run.
If `WORKSPACE/channel.json` is missing create it:
`{"name": "<folder>", "voice": {"engine": "edge", "voice": "hi-IN-MadhurNeural", "rate": "+6%", "pitch": "-6Hz"}, "length_min": 10, "res": "1080", "used_titles": []}`
(ElevenLabs if `ELEVENLABS_API_KEY` is set — see voice.md.)

## Step 1 — topic & title
Pick a history story with a hook (money, betrayal, empire, "kaise", "kyun"). Propose 3–5 Hinglish titles
(curiosity gap, ≤60 chars), choose one (autopilot: the strongest), add it to `used_titles`.

## Step 2 — research → `research/FACTS.md`
Use WebSearch/WebFetch. 25–40 facts with year, number, source URL and safe Hindi wording.
Find 2–4 **real public-domain documents** (Wikimedia Commons, Internet Archive, Library of Congress,
British Library open collections, archive.org scans): use the Commons API (`action=query&prop=imageinfo`)
to get licence + URL; for PDFs use page thumbnails at standard widths (330 / 1280 px). Save to
`assets/docs/` or `<project>/docs/` and record title/url/licence in credits.json. Never fake a document.

## Step 3 — script → `SCRIPT.md`, then `story.json`
Follow script-template.md: **click confirmation in the first 5 s, hook + open loop by 30 s, honest FOMO
(open loops, chapter cliffhangers, next-part loop), ≥90 % high-value lines, but/therefore pacing, title answered
plainly, CTA only after the payoff**. Tag beats in SCRIPT.md ([CC] [HOOK] [LOOP+] [FOMO] [HV] [PROOF] [PAYOFF] [CTA]).
Run the `itihaas-cartoon-studio:script-doctor` agent and apply its replacements until every score is ≥ 8.
Convert to story.json (scenes.md): one beat per line (2.5–5 s), set + 2–3 camera angles per location,
characters with gestures, a device in most beats (board, bubble, emph, popup, table, window, names),
`realdoc` for every proof, `source` on every fact shot, black cards for chapters/punchlines, India maps as full outline.
Launch the `itihaas-cartoon-studio:fact-checker` agent on SCRIPT.md + FACTS.md and apply its fixes.

## Step 4 — voice & audio
Voice choice (voice.md): `ELEVENLABS_API_KEY` set → engine elevenlabs (route A); ElevenLabs connector available →
route B (generate each line from `el_lines.py --json`, save to `audio/own/<id>.mp3`); otherwise free Edge.
User gave ONE voiceover file → `python "<ENGINE>/split_vo.py" <project> <file>` (check its table; `--cuts` to fix).
Give dialogue beats `"tags"` ([angry], [excited], [whispers]) for ElevenLabs v3/v4.
`python "<ENGINE>/voice.py" <project>` (prints minutes, wpm) → adjust beats if length is off by >8%.
`python "<ENGINE>/audio.py" <project>` (music bed + auto SFX at sfx_volume, ducked under voice).

## Step 5 — preview & fix (never skip)
`python "<ENGINE>/render.py" <project> --preview --res 360` → read every `out/preview_XX.jpg`.
Fix: cut-off text, characters overlapping, empty frames, the same framing 3× in a row, unreadable labels.
Re-preview only changed beats with `--only s05,s06`.

## Step 6 — render
`python "<ENGINE>/render.py" <project> --res 1080` (background; shots are cached, `--fresh` after engine changes).
Termux/phone: `--res 720`. Check with ffprobe + 8 extracted frames (Read them).

## Step 7 — upload pack
`python "<ENGINE>/meta.py" <project>` → title, description with chapters + sources, tags, pinned comment, SRT.
Report: title, length, final video path, upload folder, sources used and anything not verified.
Never upload anywhere unless the user explicitly asks.
