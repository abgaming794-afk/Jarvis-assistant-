# Voices

`story.json` → `voice` (default for every beat) + `speakers` (per-speaker overrides; each beat picks one with
`"speaker"`). Optional per-beat `"tags"` (e.g. `"[angry]"`, `"[whispers] [pause]"`) are used by ElevenLabs v3/v4.

| engine | setup | notes |
|---|---|---|
| `edge` (free, default) | nothing | hi-IN-MadhurNeural, hi-IN-SwaraNeural, and more natural multilingual voices that read Devanagari: en-US-AndrewMultilingualNeural, en-US-BrianMultilingualNeural, en-AU-WilliamMultilingualNeural, fr-FR-RemyMultilingualNeural, en-US-AvaMultilingualNeural (female). Tune with `rate` / `pitch` |
| `elevenlabs` (paid, best) | route A or B below | per speaker `"elevenlabs": {"voice_id": "...", "model": "eleven_v4", "settings": {...}}` |
| `own` | files in `<project>/audio/own/<beat id>.mp3` | your recordings or exports, one file per beat |

**Any file in `audio/own/<id>.mp3|wav|m4a` always wins** for that beat (set `"use_own_if_present": false` to disable),
so you can mix: most lines from Edge/ElevenLabs, a few re-recorded by hand.

## One full voiceover file (ElevenLabs export, own recording, upload)
Record / generate the whole script in story.json order with a short pause (~1 s) between lines, then
`python split_vo.py <project> vo.mp3` → writes `audio/own/<id>.wav` for every beat. It matches the pauses to the
script structure (spoken length per beat + sentence breaks), prints a table and flags `<-- check` beats.
If a cut is wrong, pass exact start times of beats 2..N: `--cuts 6.5,12.4,...` (its guess is in `audio/own/_cuts.txt`).

## ElevenLabs — route A: API key (fully automatic)
1. ElevenLabs website → Profile → API keys → create a key.
2. Set it before running: `export ELEVENLABS_API_KEY=...` (Termux/Mac/Linux) or `setx ELEVENLABS_API_KEY ...` (Windows).
3. In story.json set `"voice": {"engine": "elevenlabs"}` (speakers keep their `elevenlabs.voice_id`).
4. `python el_lines.py <project>` shows what will be generated and the credit estimate; then `python voice.py <project>`.
If the account runs out of credits voice.py stops with a clear message (no retries, no surprise charges).

## ElevenLabs — route B: the ElevenLabs connector inside Claude (no key needed)
For Claude with the ElevenLabs connector enabled:
1. `python el_lines.py <project> --json` → list of {id, voice_id, model, prompt, done}.
2. Optionally price one line first (`creative_generate_speech` with `estimate_only: true`) and tell the user the
   total (≈ characters on eleven_v4). If credits are 0, stop and say so.
3. For each line not done: `creative_generate_speech` (model from the list, voice_id, prompt, `generations_count: 1`,
   one shared `flow_id` from `creative_create_flow`), poll `creative_get_flow_run_status`, download the finished
   audio to `<project>/audio/own/<id>.mp3`. Never re-run a generation to "retry" — it charges again.
4. `python voice.py <project>` picks the files up; continue with audio.py / render.py.

## Recommended Hindi ElevenLabs voices (from the voice library)
| role | voice | voice_id |
|---|---|---|
| narrator (deep storyteller) | Kamal – Storyteller and Narrator | EppcM8bFS2tfl4Xu0tpj |
| suspense narrator | Shivank – Deep, Breathy and Suspense | wbOlq3nIga8HKqcDhASI |
| angry / gruff man | Niraj – Angry, Annoyed Character | 7EvySNHBey9ISwbL5Bt5 |
| young energetic man | Bunty – Funny Best Friend | 7b9mYhmnp0y2qSH1FnBL |
| expressive middle-aged man | Sunil SL Narnauliya | n4jGuG5wrMvqWCjMtnMS |
| mature woman / queen | Devika – Warm Hindi Narrator | MaJjkQJkKTqVB1XVQopL |

Only changed beats are re-recorded. `voice.py` prints minutes and words/min; aim 160–170 wpm.
