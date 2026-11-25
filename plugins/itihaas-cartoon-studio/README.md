# Itihaas Cartoon Studio (Claude Code plugin)

Hindi history explainer videos A to Z in the documentary-toon style: minimal cartoon characters in lit vector
sets, 2.5D parallax camera, seamless transitions, character dialogue with different voices, real archival
documents in 3D with paper curl and SOURCE credits, top-down "money on the table" scenes, split screens,
maps that always show India's full official outline.

Commands after install:
- `/itihaas-cartoon-studio:make-video "Plassey ki ladai" 10 1080` — full video on autopilot
- `/itihaas-cartoon-studio:demo 360` — renders the bundled 90-second East India Company demo
- or just ask: "itihaas cartoon studio se Plassey par 10 minute ka video banao"

---

## 1. Install on a computer (Windows / Mac / Linux)
Needs: Claude Code, Python 3.10+, git. (ffmpeg is installed automatically by `doctor.py --fix`.)

```bash
git clone -b claude/youthful-planck-84mlz8 https://github.com/abgaming794-afk/Jarvis-assistant-.git
cd Jarvis-assistant-
claude
```
Inside Claude Code:
```
/plugin marketplace add ./
/plugin install itihaas-cartoon-studio@itihaas-studio
```
Restart Claude Code, then run `/itihaas-cartoon-studio:demo 360`.

## 2. Install on Android with Termux
Install **Termux from F-Droid** (the Play Store build is outdated). Then in Termux:

```bash
pkg update -y && pkg upgrade -y
pkg install -y git python ffmpeg nodejs-lts python-pillow python-numpy
pip install edge-tts certifi
npm install -g @anthropic-ai/claude-code
termux-setup-storage
git clone -b claude/youthful-planck-84mlz8 https://github.com/abgaming794-afk/Jarvis-assistant-.git
cd Jarvis-assistant-
claude
```
Inside Claude Code run the same two `/plugin …` lines as above, then `/itihaas-cartoon-studio:demo 360`.

Phone tips
- Render at `720` (or `360` for previews); 1080p works but is slow on a phone.
- Copy the finished video to your gallery: `cp videos/<name>/out/*.mp4 ~/storage/downloads/`
- Claude Code on Termux is community-supported, not official. If it will not start, you can still run the
  engine directly (section 3) and use Claude on the web/app for writing the script.

## 3. Use the engine without Claude
```bash
E=plugins/itihaas-cartoon-studio/skills/itihaas-cartoon-studio/engine
python $E/doctor.py --fix
mkdir -p videos/demo && cp plugins/itihaas-cartoon-studio/skills/itihaas-cartoon-studio/examples/eic-founding.json videos/demo/story.json
python $E/voice.py videos/demo
python $E/audio.py videos/demo
python $E/render.py videos/demo --preview --res 360    # contact sheets in out/
python $E/render.py videos/demo --res 720              # out/final_720p.mp4
python $E/meta.py videos/demo                          # upload/ pack
```

## Voices
- Free Edge voices by default.
- **ElevenLabs (automatic):** `export ELEVENLABS_API_KEY=your_key`, set `"voice": {"engine": "elevenlabs"}` in story.json.
  Each speaker already has a Hindi ElevenLabs voice and emotion tags; `python $E/el_lines.py videos/<name>` shows the
  lines and credit estimate. Without a key, Claude can use the ElevenLabs connector instead (references/voice.md).
- Own recordings: drop `s01.mp3 …` into `videos/<name>/audio/own/` — they are used automatically.

## Rules built in
- India is always drawn with its full official map (J&K incl. PoK/Gilgit-Baltistan, Ladakh incl. Aksai Chin, Arunachal).
- Documents shown as proof are real public-domain scans with credits (`assets/docs/credits.json`).
- The plugin copies an editing *style*; characters, scripts and artwork are original.

## Licences of bundled assets
Fonts: Montserrat, Caveat, Kalam (SIL OFL), Permanent Marker (Apache 2.0). Map data: Natural Earth (public domain).
Documents: see `assets/docs/credits.json` (public domain).
