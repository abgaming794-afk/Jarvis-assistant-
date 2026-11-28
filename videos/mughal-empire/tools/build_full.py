"""story.json for the WHOLE film: demo beats (build_v3) + every line of script_full/lines.json directed in
tools/dir_*.py. Consecutive specs in the same set form one continuous camera shot; set changes get a 3D wipe
(mostly the pillar). Overlays (_ov) float over the running scene. Run after the voice so timings are real."""
import copy, json, os, subprocess, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, P + "/studio/engine"); sys.path.insert(0, P + "/tools")
r = subprocess.run([sys.executable, P + "/tools/build_v3.py"], capture_output=True, text=True)
if r.returncode:
    print(r.stdout[-2000:], r.stderr[-3000:]); sys.exit("build_v3 failed")
story = json.load(open(P + "/story.json", encoding="utf-8"))
import set3d  # noqa: E402
import dirlib, dir_c1_2, dir_c3_4, dir_c5_6, dir_c7_9  # noqa: E402

L = json.load(open(P + "/script_full/lines.json", encoding="utf-8"))
CH = {1: dir_c1_2.SHOTS, 2: dir_c1_2.SHOTS2, 3: dir_c3_4.SHOTS3, 4: dir_c3_4.SHOTS4, 5: dir_c5_6.SHOTS5, 6: dir_c5_6.SHOTS6,
      7: dir_c7_9.SHOTS7, 8: dir_c7_9.SHOTS8, 9: dir_c7_9.SHOTS9}
specs, bad = [], []
for ch, shots in CH.items():
    sp = [s for _, lst in shots for s in lst]
    n = sum(1 for x in L if x["chapter"] == ch)
    if len(sp) != n:
        bad.append(f"chapter {ch}: {len(sp)} specs for {n} lines")
    specs += sp
if bad:
    sys.exit("COUNT MISMATCH\n" + "\n".join(bad))

timing = (json.load(open(P + "/audio/timing.json")) if os.path.exists(P + "/audio/timing.json") else {"beats": {}})["beats"]
dur_of = lambda x: timing[x["id"]]["dur"] if x["id"] in timing else max(2.5, len(x["text"].split()) / 2.5 + 0.4)

# ------------------------------------------------------------------ beats
beats, year = [], 1527
for x, sp in zip(L, specs):
    sp = copy.deepcopy(sp)
    year = sp.pop("_y", year)
    sp.pop("_set", None)
    b = {"id": x["id"], "speaker": "N" if x["who"] == "N" else x["who"], "text": x["text"], "year": year,
         "chapter_tag": x["chapter_title"]}
    if "_ov" in sp:
        b["_ov"] = sp.pop("_ov")
    if sp.get("set") and not sp.get("global_map"):
        if sp["set"] == "study":          # keep people in front of the desk (desk spans z 4.7-5.7)
            for a in sp.get("actors", []):
                if a.get("z", 0) > 4.2 and not a.get("y"):
                    a["z"] = 4.0
        if sp.get("big") or sp.get("chapter_card"):   # leave the top band free for the big kinetic text
            _, _, dflt = set3d.build(sp["set"], sp)
            tg = list(sp.get("target", dflt["target"]))
            sp["target"] = [tg[0], tg[1] + 0.35, tg[2]]
            sp["dist"] = sp.get("dist", dflt["dist"]) * 1.18
    b["_spec"] = sp
    beats.append(b)

# ------------------------------------------------------------------ segment into continuous shots
def set_of(sp):
    return "map" if sp.get("global_map") else sp.get("set")

segs = []
for b in beats:
    if "_ov" in b and not {k for k in b["_spec"] if not k.startswith("_")}:
        if not segs:
            sys.exit("overlay before any scene")
        segs[-1][1].append(b)
        continue
    loc = set_of(b["_spec"])
    if not segs or segs[-1][0] != loc or b["_spec"].get("_cut"):
        segs.append((loc, [b]))
    else:
        segs[-1][1].append(b)

STRIP = ("big", "board", "names", "stickers", "bubble", "emph", "swoosh", "popup", "source", "source_by", "days_left", "month_cal",
         "caption", "chapter_card")


def same(a, b, key):
    return a.get(key) == b.get(key) and abs(a.get("x", 0) - b.get("x", 0)) < 0.6 and abs(a.get("z", 0) - b.get("z", 0)) < 0.6


prev_scene = story["beats"][-1]["scene"]
for loc, bs in segs:
    scenes = []
    for b in bs:
        if "_ov" in b:
            base = copy.deepcopy(scenes[-1] if scenes else prev_scene)
            for k in STRIP:
                base.pop(k, None)
            for a in base.get("actors", []) + base.get("objs", []):
                for f in ("exit", "fade_in", "delay", "anim", "enter", "to"):
                    a.pop(f, None)
            for k in ("path", "keys", "enter_tr", "exit_tr"):
                base.pop(k, None)
            base["overlay"] = b.pop("_ov")
            base["_cont"] = True
            sc = base
        else:
            sc = b["_spec"]
            sc.pop("_cut", None)
        sc["type"] = "set3d"
        if loc == "map":
            sc["set"] = "map"; sc["global_map"] = True
        else:
            sc["set"] = loc
        scenes.append(sc)
    # actors / props carried across beats of the same shot fade instead of popping
    for i in range(1, len(scenes)):
        cur, pv = scenes[i], scenes[i - 1]
        if cur.get("_cont"):
            continue
        for key, lst in (("who", "actors"), ("prop", "objs")):
            prev_items = [a for a in pv.get(lst, []) if not a.get("exit")]
            for a in cur.get(lst, []):
                if not any(same(a, p, key) for p in prev_items):
                    a.setdefault("fade_in", True)
            for p in prev_items:
                if not any(same(a, p, key) for a in cur.get(lst, [])):
                    q = copy.deepcopy(p)
                    for f in ("fade_in", "delay", "anim", "enter"):
                        q.pop(f, None)
                    if q.get("to") is not None:
                        q["x"], q["z"] = q["to"][0], q["to"][1]; q.pop("to")
                    q["exit"] = True
                    cur.setdefault(lst, []).append(q)
    F = []
    for sc in scenes:
        if loc == "map" and sc.get("view"):
            F.append(set3d.view_key(sc["view"]))
        elif sc.get("_cont") and F:
            k = list(F[-1]); k[3] *= 0.94; F.append(k)
        elif sc.get("_cont"):
            _, _, dflt = set3d.build(sc["set"], sc); F.append(set3d.key_of(sc, dflt))
        else:
            _, _, dflt = set3d.build(sc["set"], sc); F.append(set3d.key_of(sc, dflt))
    S = [0.0]
    for b in bs:
        S.append(S[-1] + dur_of(b))
    n = len(F)
    lerp = lambda a, c, t: [p + (q - p) * t for p, q in zip(a, c)]
    K = [None] * (n + 1)
    K[0] = list(F[0]); K[0][3] *= 1.18; K[0][4] *= 1.05
    for j in range(1, n):
        K[j] = lerp(F[j - 1], F[j], 0.7)
    K[n] = list(F[-1]); K[n][3] *= 0.88
    for i, sc in enumerate(scenes):
        sc["path"] = {"F": F, "S": S, "i": i}
        sc["keys"] = [K[i - 1] if i >= 1 else K[i], K[i], K[i + 1], K[i + 2] if i + 2 <= n else K[i + 1]]
        sc.pop("cam", None); sc.pop("_cont", None)
    for b, sc in zip(bs, scenes):
        b["scene"] = sc
        b.pop("_spec", None)
    prev_scene = scenes[-1]

# ------------------------------------------------------------------ 3D wipes between shots (pillar = favourite)
ROT = ["wipe", "wipe_flag", "wipe", "wipe_curtain", "wipe", "doors", "wipe", "wipe_army", "wipe", "wipe_elephant", "wipe", "wipe_curtain",
       "wipe", "wipe_flag", "clouds"]
last = story["beats"][-1]
firsts = [bs[0] for _, bs in segs]
lasts = [last] + [bs[-1] for _, bs in segs[:-1]]
for j, (a, b) in enumerate(zip(lasts, firsts)):
    kind = ROT[j % len(ROT)]
    if kind == (a["scene"].get("enter_tr")):
        kind = "wipe" if kind != "wipe" else "wipe_curtain"
    a["scene"]["exit_tr"] = kind
    b["scene"]["enter_tr"] = kind

# missing archive images (downloads can lag): drop that medallion / turn the doc into a text card, rebuild later
for b in beats:
    sc = b["scene"]
    m = sc.get("map") or {}
    if m.get("medallions"):
        m["medallions"] = [md for md in m["medallions"] if os.path.exists(md["img"])]
    ov = sc.get("overlay")
    if ov and ov.get("type") == "realdoc" and not os.path.exists(ov["img"]):
        sc["overlay"] = {"type": "black", "t": ov.get("source", "")[:90]}
        print("  (missing image, text card for now)", b["id"], os.path.basename(ov["img"]))
story["beats"] += beats
story["cast"].update(dirlib.CAST)
json.dump(story, open(P + "/story.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = sum(dur_of({"id": b["id"], "text": b["text"]}) for b in story["beats"])
print(len(story["beats"]), "beats ·", len(segs), "new shots ·", sum(1 for b in beats if b["scene"].get("overlay")), "overlays ·",
      f"~{tot / 60:.1f} min")
