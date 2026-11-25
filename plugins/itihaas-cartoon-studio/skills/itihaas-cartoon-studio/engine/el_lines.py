"""ElevenLabs job list for a project.  python el_lines.py <project> [--json]

Shows, per beat, the speaker, voice_id, model and the exact prompt (inline tags + text) to generate, whether
audio/own/<id>.* already exists, and the character count (≈ credits). Used for the connector route: generate each
line with the ElevenLabs connector (creative_generate_speech, 1 take), download it to audio/own/<id>.mp3, then run
voice.py — files in audio/own are picked up automatically.
"""
import json, os, sys
from common import load_json
from voice import el_prompt


def main():
    proj = os.path.abspath(sys.argv[1])
    story = load_json(os.path.join(proj, "story.json"))
    base = dict(story.get("voice", {}))
    speakers = story.get("speakers", {})
    rows, chars = [], 0
    for b in story["beats"]:
        cfg = dict(base)
        cfg.update(speakers.get(b.get("speaker", "N"), {}))
        el = dict(cfg, **cfg.get("elevenlabs", {}))
        model = el.get("model", "eleven_v4")
        prompt = el_prompt(b["text"], b.get("tags", ""), model)
        have = any(os.path.exists(os.path.join(proj, "audio", "own", b["id"] + e)) for e in (".mp3", ".wav", ".m4a"))
        if not have:
            chars += len(prompt)
        rows.append({"id": b["id"], "speaker": b.get("speaker", "N"), "voice_id": el.get("voice_id"),
                     "model": model, "prompt": prompt, "done": have})
    if "--json" in sys.argv:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
    else:
        for r in rows:
            print(f"{r['id']}  {'DONE' if r['done'] else 'todo'}  {r['speaker']:3} {r['voice_id'] or '-':22} {r['model']:22} {r['prompt']}")
    todo = sum(1 for r in rows if not r["done"])
    print(f"\n{todo} lines to generate, ~{chars} characters (~{chars} credits on eleven_v4)")


if __name__ == "__main__":
    main()
