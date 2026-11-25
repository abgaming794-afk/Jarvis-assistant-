"""Setup / health check.  python doctor.py [--fix]

Checks Python packages (Pillow, numpy, edge-tts, certifi), ffmpeg and the bundled fonts/data.
--fix installs what is missing with pip (and imageio-ffmpeg for a bundled ffmpeg).
On Termux (Android) Pillow/numpy/ffmpeg come from `pkg`, so the exact commands are printed instead.
"""
import importlib, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
TERMUX = "com.termux" in os.environ.get("PREFIX", "") or os.path.isdir("/data/data/com.termux")
PKGS = {"PIL": "Pillow", "numpy": "numpy", "edge_tts": "edge-tts", "certifi": "certifi"}
OPTIONAL = {"edge_tts", "certifi"}   # only for the free online voice; not needed with your own / uploaded VO


def have(mod):
    try:
        importlib.import_module(mod)
        return True
    except Exception:
        return False


def ffmpeg():
    p = shutil.which("ffmpeg")
    if p:
        return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def main():
    fix = "--fix" in sys.argv
    missing = [pip for mod, pip in PKGS.items() if not have(mod) and mod not in OPTIONAL]
    opt_missing = [pip for mod, pip in PKGS.items() if not have(mod) and mod in OPTIONAL]
    ff = ffmpeg()
    print(f"python   {sys.version.split()[0]}  ({'Termux' if TERMUX else sys.platform})")
    for mod, pip in PKGS.items():
        print(f"{pip:9}{'OK' if have(mod) else ('missing (optional: free online voice)' if mod in OPTIONAL else 'MISSING')}")
    print(f"ffmpeg   {ff or 'MISSING'}")
    print(f"ElevenLabs API key  {'set' if os.environ.get('ELEVENLABS_API_KEY') else 'not set (free Edge voices, or the ElevenLabs connector route)'}")
    for f in ("assets/fonts/Caveat-Variable.ttf", "assets/fonts/Kalam-Bold.ttf", "engine/data/world.geojson",
              "engine/data/india_full.geojson"):
        print(f"{f:40}{'OK' if os.path.exists(os.path.join(SKILL, f)) else 'MISSING'}")
    if not missing and ff:
        if opt_missing and fix:
            subprocess.call([sys.executable, "-m", "pip", "install", "--quiet", *opt_missing])
        print("\nREADY" + ("  (no edge-tts: use your own / ElevenLabs VO, e.g. split_vo.py)" if opt_missing and not all(
            have(m) for m in OPTIONAL) else ""))
        return 0
    if TERMUX:
        print("\nTermux: run these once, then run doctor.py again:")
        print("  pkg install -y python ffmpeg python-pillow python-numpy")
        print("  pip install edge-tts certifi")
        return 1
    if fix:
        need = list(missing) + ([] if ff else ["imageio-ffmpeg"])
        print("\ninstalling:", " ".join(need))
        subprocess.call([sys.executable, "-m", "pip", "install", "--quiet", *need])
        os.execv(sys.executable, [sys.executable, __file__])
    print("\nNOT READY - run: python doctor.py --fix")
    return 1


if __name__ == "__main__":
    sys.exit(main())
