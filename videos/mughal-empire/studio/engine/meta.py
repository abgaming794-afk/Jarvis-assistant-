"""Upload pack.  python meta.py <project> [--fps 30]

Writes <project>/upload/: title.txt, description.txt (with chapters from real timestamps + sources),
tags.txt, pinned_comment.txt, captions.srt (narration and dialogue lines with real timings).
Uses story.json keys: title, description, tags, pinned_comment, sources (list of {"t","url"}) and
beats[].chapter / scene.source.
"""
import os, sys
from common import load_json


def ts(sec, srt=False):
    h, m = int(sec // 3600), int(sec % 3600 // 60)
    s = sec % 60
    if srt:
        return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"
    return f"{h}:{m:02d}:{int(s):02d}" if h else f"{m}:{int(s):02d}"


def main():
    proj = os.path.abspath(sys.argv[1])
    fps = int(sys.argv[sys.argv.index("--fps") + 1]) if "--fps" in sys.argv else 30
    story = load_json(os.path.join(proj, "story.json"))
    timing = load_json(os.path.join(proj, "audio", "timing.json"), {"beats": {}})
    up = os.path.join(proj, "upload")
    os.makedirs(up, exist_ok=True)
    t, chapters, srt, sources = 0.0, [], [], []
    for i, b in enumerate(story["beats"]):
        tb = timing["beats"].get(b["id"], {})
        dur = max(1, round(tb.get("dur", 3) * fps)) / fps
        if b.get("chapter"):
            chapters.append((0.0 if not chapters else t, b["chapter"]))
        v = tb.get("voice", dur)
        srt.append(f"{len(srt) + 1}\n{ts(t + .06, True)} --> {ts(t + .06 + v, True)}\n{b['text']}\n")
        src = b.get("scene", {}).get("source")
        if src and src not in sources:
            sources.append(src)
        t += dur
    for s in story.get("sources", []):
        line = f"{s['t']} — {s['url']}" if isinstance(s, dict) else str(s)
        if line not in sources:
            sources.append(line)
    title = story.get("title", "Untitled")
    desc = [story.get("description", title), ""]
    if len(chapters) >= 3:
        desc += ["Chapters"] + [f"{ts(c)} {n}" for c, n in chapters] + [""]
    if sources:
        desc += ["Sources"] + [f"• {s}" for s in sources] + [""]
    desc += ["Animated in-house. Historical documents are public-domain scans; dialogue is dramatised."]
    files = {
        "title.txt": title,
        "description.txt": "\n".join(desc),
        "tags.txt": ", ".join(story.get("tags", [])),
        "pinned_comment.txt": story.get("pinned_comment", ""),
        "captions.srt": "\n".join(srt),
    }
    for k, v in files.items():
        with open(os.path.join(up, k), "w", encoding="utf-8") as f:
            f.write(v)
    print(f"UPLOAD PACK OK: {up}  ({len(chapters)} chapters, {len(sources)} sources, {len(srt)} captions)")


if __name__ == "__main__":
    main()
