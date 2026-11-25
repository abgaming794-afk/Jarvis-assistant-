# Voices

`story.json` → `voice` (default for every beat) + `speakers` (per-speaker overrides; beats choose with `"speaker"`).

| engine | setup | notes |
|---|---|---|
| `edge` (free) | nothing | voices: hi-IN-MadhurNeural, hi-IN-SwaraNeural, and the more natural multilingual voices en-US-AndrewMultilingualNeural, en-US-BrianMultilingualNeural, en-AU-WilliamMultilingualNeural, fr-FR-RemyMultilingualNeural, en-US-AvaMultilingualNeural (female) — they read Devanagari. Tune with `rate` "+6%" / `pitch` "-6Hz" |
| `elevenlabs` (paid) | env `ELEVENLABS_API_KEY`, per speaker `voice_id`, `model` (eleven_v4 / eleven_multilingual_v2) | best quality; eleven_v4 understands tags like `[angry]`, `[whispers]`, `[pause]` inside `text`. Hindi voices that fit: narrator "Kamal – Storyteller" (EppcM8bFS2tfl4Xu0tpj), angry merchant "Niraj" (7EvySNHBey9ISwbL5Bt5), young "Bunty" (7b9mYhmnp0y2qSH1FnBL), expressive "Sunil" (n4jGuG5wrMvqWCjMtnMS), mature woman "Devika" (MaJjkQJkKTqVB1XVQopL) |
| `own` | put recordings in `<project>/audio/own/<beat id>.mp3` (or .wav) | your own or ElevenLabs-website exports, one file per beat |

Only changed beats are re-recorded. `voice.py` prints minutes and words/min; aim 160–170 wpm.
Silence at both ends of each line is trimmed automatically; `pause` (story) / `pause` (beat) adds air after a line.
