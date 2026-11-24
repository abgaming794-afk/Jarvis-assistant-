"""16-second demo of the story-then-proof style (storyproof.py) on the Khilafat topic.

  python3 demo.py stills out_dir 1.0 3.0 6.0 ...      -> PNG stills (1280x720)
  python3 demo.py video out.mp4 [width=1280] [fps=30]  -> MP4 (H.264)

Beats: satellite flight to Sindh + glowing region + pin 'Debal 711' -> white Umayyad banner fills Sindh ->
timeline 711 -> 739 -> hard wipe to the parchment map -> map mascots (eyes), arrow to Navsari, banner peels off,
stamp 'ROK DIYA!' with camera shake -> ink iris -> story scene (photoreal AI battle, push-in, crowd, serif title)
-> the REAL proof: Wikipedia page flies in, camera pans to the line and the marker highlights it.
The channel's own 2D man is added by the project storyboard (not part of this demo)."""
import os, sys, json, math, subprocess
DEMO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DEMO, "..", "..", "visuals"))
import numpy as np, skia
from PIL import Image
from core import *
from storyproof import *

WM = WorldMap()
SAT = Satellite(0, 150, -35, 65)
BATTLE = sk_image(Image.open(os.path.join(DEMO, "battle_photoreal.jpg")))
DOC = sk_image(Image.open(os.path.join(DEMO, "navsari.png")))
DJ = json.load(open(os.path.join(DEMO, "navsari.json")))
ln = DJ["lines"][0][0]; DW_, DH_ = DOC.width(), DOC.height()
HL = (ln["x0"] / DW_, (ln["y"] - ln["h"] * 0.05) / DH_, ln["x1"] / DW_, (ln["y"] + ln["h"] * 0.95) / DH_)   # json y = top of the line

def banner_img(w=600, h=400):                         # plain white Umayyad banner (historically white), soft cloth folds
    a = np.full((h, w, 4), 255, np.uint8); xs = np.arange(w)
    shade = (235 + 20 * np.sin(xs / w * 6 * math.pi)).astype(np.uint8)
    a[..., 0] = a[..., 1] = a[..., 2] = shade[None, :]; return skia.Image.fromarray(a, colorType=skia.ColorType.kRGBA_8888_ColorType)
BANNER = banner_img()
END = 16.0
C_WIDE, C_SINDH, C_GUJ = (75, 25, 13.5), (69.5, 25.0, 34), (71.5, 23.5, 30)

def frame(c, t):
    P = lambda cam: WM.paths(cam[2])
    if t < 5.2:                                                         # ---------- satellite part
        cam = cam_lerp(C_WIDE, C_SINDH, seg(t, 0.0, 2.2))
        def sat_scene(cc, cam=cam):
            SAT.draw(cc, cam)
            pak = P(cam)["PAK"]
            region_glow(cc, cam, pak, seg(t, 1.2, 1.9) * (1 - seg(t, 2.3, 2.8)), t)
            flag_fill(cc, cam, pak, BANNER, seg(t, 2.3, 3.4), t, direction=(1, 0))
            x, y = to_screen(cam, 67.4, 24.75); pin_drop(cc, x, y, "Debal", "711 CE", seg(t, 1.6, 2.4), t)
            if t > 2.6:
                pos = lerp(0, 2, ease_io(seg(t, 3.5, 4.4))); vel = (seg(t, 3.5, 4.4) > 0) * (seg(t, 3.5, 4.4) < 1) * 1.0
                timeline_ribbon(cc, [711, 724, 739], pos, y=96, spacing=200, vel=vel, a=int(255 * seg(t, 2.6, 3.0)))
        if t < 4.4: sat_scene(c)
        else:
            def parch(cc): parch_scene(cc, t)
            style_wipe(c, seg(t, 4.4, 5.2), sat_scene, parch, to_left=True)
        return
    if t < 8.9:                                                         # ---------- parchment part
        parch_scene(c, t)
        iris(c, seg(t, 7.9, 8.5) if t < 8.6 else 1 - seg(t, 8.6, 8.9), t=t)
        return
    if t < 12.4:                                                        # ---------- story scene + proof fly-in
        story_scene(c, BATTLE, t, 8.6, 4.0, push=(1.0, 1.10), focus=(0.62, 0.55))
        crowd_silhouettes(c, 9, DH - 40, t, size=150)
        serif_title(c, "Navsari", DW / 2, 190, 120, seg(t, 9.2, 10.4) * (1 - seg(t, 11.0, 11.3)), date="739 CE", align="c")
        if t < 8.9: iris(c, 1 - seg(t, 8.6, 8.9), t=t)
        if t > 11.0:
            c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(120 * seg(t, 11.0, 11.4))))
            doc_fly(c, DOC, seg(t, 11.0, 11.9), (DW / 2 - 640, DH / 2 - 301, DW / 2 + 640, DH / 2 + 301))
        return
    k = seg(t, 12.4, 13.0)                                              # ---------- proof: pan + highlight
    wn = (HL[2] - HL[0]) + 0.16; hn = wn * (DW_ / DH_) * 9 / 16                 # 16:9 window around the line
    cxn, cyn = (HL[0] + HL[2]) / 2, (HL[1] + HL[3]) / 2
    r0 = (0.0, 0.0, 1.0, 1.0); r1 = (cxn - wn / 2, cyn - hn / 2, cxn + wn / 2, cyn + hn / 2)
    doc_pan(c, DOC, t, 12.4, 1.6, r0, r1, highlights=[HL + (14.1, 14.9)])
    c.drawRect(skia.Rect(0, 0, DW, DH), paint("#000000", int(140 * (1 - k))))
    footnote(c, "Saboot: en.wikipedia.org - Caliphate campaigns in India")

def parch_scene(c, t):
    cam = cam_lerp(C_SINDH, C_GUJ, seg(t, 5.0, 6.4))
    P = WM.paths(cam[2])
    parchment_map(c, WM, cam, fills={"IND": ("#E8A23A", 200)})
    pak = P["PAK"]
    if t < 6.6: flag_fill(c, cam, pak, BANNER, 1.0, t, direction=(1, 0))
    else: flag_peel(c, cam, pak, BANNER, seg(t, 6.6, 7.6), direction=(1, 0.3))
    ix, iy = to_screen(cam, 77.5, 22.5); googly_eyes(c, ix, iy, 26, t, look=(-0.8, 0.1), mood="angry", k=seg(t, 5.4, 5.8))
    px, py = to_screen(cam, 68.5, 27.0); googly_eyes(c, px, py, 20, t, look=(0.6, 0.4), mood="scared", k=seg(t, 5.7, 6.1))
    nx, ny = to_screen(cam, 72.95, 20.95)
    white_arrow(c, nx - 40, ny - 40, ang=45, size=90, t=t, k=seg(t, 6.0, 6.4))
    text(c, "Navsari", nx + 18, ny + 10, 34, "#2B1D0E", SERIF_DISPLAY, "l", int(255 * seg(t, 6.1, 6.5)))
    dx, dy = shake(t, 7.05, 14)
    c.save(); c.translate(dx, dy)
    stamp_slam(c, "ROK DIYA!", nx + 230, ny + 120, 70, seg(t, 6.9, 7.3))
    c.restore()

def render(t, width=1280):
    surf = skia.Surface(width, int(width * 9 / 16)); c = surf.getCanvas(); c.scale(width / DW, width / DW)
    c.clear(hexc("#000000")); frame(c, t)
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        for ts in sys.argv[3:]: Image.fromarray(render(float(ts))).convert("RGB").save(os.path.join(out, f"t{float(ts):05.2f}.png"))
    else:
        out = sys.argv[2]; width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280; fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
        h = int(width * 9 / 16)
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{width}x{h}", "-r", str(fps), "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
        for f in range(int(END * fps)): ff.stdin.write(render(f / fps, width).tobytes())
        ff.stdin.close(); ff.wait(); print("demo ok", out)
