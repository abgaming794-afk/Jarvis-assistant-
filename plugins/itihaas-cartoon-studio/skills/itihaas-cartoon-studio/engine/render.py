"""Renders story.json to out/final.mp4.

python render.py <project> [--res 360|720|1080] [--fps 30] [--preview] [--only b001,b002] [--fresh] [--workers N]

--preview  -> out/preview_XX.jpg contact sheets (one labelled still per beat), no video.
Shots are cached in work/seg_<res>/ by a hash of the beat + cast + engine version, so after editing a few
beats only those are re-rendered.
"""
import os, sys, json, hashlib, subprocess, time
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw
from common import load_json, ffmpeg_bin, font

ENGINE_VERSION = "2.0.0"
RES = {"360": (640, 360), "480": (854, 480), "720": (1280, 720), "1080": (1920, 1080)}


def arg(name, default=None):
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return default


def _env(proj, bid):
    p = os.path.join(proj, "audio", "env", f"{bid}.npy")
    return np.load(p) if os.path.exists(p) else np.zeros(1)


def _durations(proj, story, fps):
    timing = load_json(os.path.join(proj, "audio", "timing.json"))
    out = {}
    for b in story["beats"]:
        if timing and b["id"] in timing["beats"]:
            d = timing["beats"][b["id"]]["dur"]
        else:  # no voice yet: estimate from words (Hindi ~150 wpm)
            d = max(2.5, len(b["text"].split()) / 2.5 + 0.4)
        out[b["id"]] = max(1, round(d * fps))
    return out


def make_shot(b, story, W, H, dur, env, fps):
    if story.get("style", "toon") == "toon":
        import toonshot
        return toonshot.ToonShot(b, story, W, H, dur, env, fps)
    import scenes
    return scenes.Shot(b, story, W, H, dur, env, fps)


def render_beat(job):
    proj, story, b, nframes, W, H, fps, out = job
    shot = make_shot(b, story, W, H, nframes / fps, _env(proj, b["id"]), fps)
    tmp = out + ".tmp.mp4"
    cmd = [ffmpeg_bin(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast" if H <= 720 else "medium",
           "-crf", "20" if H <= 720 else "18", "-pix_fmt", "yuv420p", "-r", str(fps), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(nframes):
        p.stdin.write(shot.frame(i / fps).tobytes())
    p.stdin.close()
    p.wait()
    if p.returncode:
        raise RuntimeError(f"ffmpeg failed on {b['id']}")
    os.replace(tmp, out)
    return b["id"]


def main():
    proj = os.path.abspath(sys.argv[1])
    story = load_json(os.path.join(proj, "story.json"))
    res = arg("--res", str(story.get("res", "1080")))
    W, H = RES[res]
    fps = int(arg("--fps", story.get("fps", 30)))
    frames = _durations(proj, story, fps)
    outdir = os.path.join(proj, "out")
    os.makedirs(outdir, exist_ok=True)

    if "--preview" in sys.argv:
        pw, ph = 480, 270
        cols, rows = 4, 4
        beats = story["beats"]
        only = arg("--only")
        if only:
            beats = [b for b in beats if b["id"] in only.split(",")]
        for s in range(0, len(beats), cols * rows):
            sheet = Image.new("RGB", (cols * pw, rows * (ph + 26)), (25, 25, 28))
            d = ImageDraw.Draw(sheet)
            for k, b in enumerate(beats[s:s + cols * rows]):
                n = frames[b["id"]]
                shot = make_shot(b, story, pw * 2, ph * 2, n / fps, _env(proj, b["id"]), fps)
                fr = shot.frame(n / fps * float(arg("--at", 0.7))).resize((pw, ph), Image.LANCZOS)
                x, y = (k % cols) * pw, (k // cols) * (ph + 26)
                sheet.paste(fr, (x, y))
                d.text((x + 4, y + ph + 4), f"{b['id']} {b.get('scene', {}).get('type', 'chars')} {n / fps:.1f}s",
                       fill=(255, 255, 255), font=font(15, "Bold"))
            p = os.path.join(outdir, f"preview_{s // (cols * rows) + 1:02d}.jpg")
            sheet.save(p, quality=88)
            print(p)
        return

    seg_dir = os.path.join(proj, "work", f"seg_{res}_{fps}")
    os.makedirs(seg_dir, exist_ok=True)
    cast = story.get("cast", {})
    jobs, segs = [], []
    only = set(arg("--only", "").split(",")) - {""}
    for b in story["beats"]:
        h = hashlib.md5(json.dumps([ENGINE_VERSION, story.get("style", "toon"), b.get("scene"), b.get("transition"), cast, frames[b["id"]],
                                    b["id"], res], sort_keys=True, default=str).encode()).hexdigest()[:10]
        out = os.path.join(seg_dir, f"{b['id']}_{h}.mp4")
        segs.append(out)
        if "--fresh" in sys.argv or not os.path.exists(out) or b["id"] in only:
            jobs.append((proj, story, b, frames[b["id"]], W, H, fps, out))
    t0 = time.time()
    workers = int(arg("--workers", max(1, (os.cpu_count() or 2))))
    print(f"rendering {len(jobs)}/{len(segs)} shots at {W}x{H} {fps}fps with {workers} workers ...")
    if jobs:
        with Pool(workers) as pool:
            for i, bid in enumerate(pool.imap_unordered(render_beat, jobs), 1):
                print(f"  [{i}/{len(jobs)}] {bid}  {time.time() - t0:.0f}s", flush=True)
    lst = os.path.join(seg_dir, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    video = os.path.join(proj, "work", f"video_{res}.mp4")
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    video], check=True)
    mix = os.path.join(proj, "audio", "mix.wav")
    final = os.path.join(outdir, "final.mp4" if res == "1080" else f"final_{res}p.mp4")
    if os.path.exists(mix):
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", video, "-i", mix, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-shortest", "-movflags", "+faststart", final], check=True)
    else:
        os.replace(video, final)
        print("note: no audio/mix.wav — run voice.py and audio.py first for sound")
    print(f"RENDER OK: {final}  ({sum(frames.values()) / fps:.1f}s, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
