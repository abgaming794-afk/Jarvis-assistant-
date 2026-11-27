# story.json v3 — one continuous camera flow.
# Beats that share a location form ONE shot: the camera follows a smooth Catmull-Rom path through every beat
# (no transitions, no cuts). Location changes fly up through clouds, over ONE global 3D map, and down again.
# Black cards / documents / charts / small maps float over the running 3D scene.
import copy, json, os, subprocess, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, P + "/studio/engine")
subprocess.run([sys.executable, P + "/tools/build_v2.py"], check=True, capture_output=True)
story = json.load(open(P + "/story.json", encoding="utf-8"))
B = {b["id"]: b for b in story["beats"]}
import set3d  # noqa: E402

GM = lambda view, **m: {"type": "set3d", "set": "map", "global_map": True, "view": view, "map": m}
IND_HL = {"IND": "#d9a72b", "PAK": "#d9a72b", "BGD": "#d9a72b", "AFG": "#c99a35"}
A = lambda who, x, z, **k: dict(who=who, x=x, z=z, **k)
O = lambda prop, x, z, **k: dict(prop=prop, x=x, z=z, **k)


def sc_of(bid):
    return copy.deepcopy(B[bid]["scene"])


def ov(kind, base_id, **k):
    """Overlay beat: continue the 3D scene of base_id, float `kind` on top."""
    return {"_overlay_of": base_id, "overlay": dict(type=kind, **k)}


def minimap(bid):
    return dict(sc_of(bid)["map"])


# ------------------------------------------------------------------ location plan
SEQ = []          # list of (location name, [beat ids])
NEW = {}          # beat id -> replacement scene (or overlay spec)

# A court 1700
NEW["s01b"] = ov("chart", "s01", **{k: v for k, v in sc_of("s01b").items() if k != "type"})
SEQ.append(("court", ["s01", "s01b"]))
# B map
NEW["s02"] = GM([60, 5, 100, 40], highlight=IND_HL,
                labels=[{"lon": 78, "lat": 25, "t": "MUGHAL HINDUSTAN", "size": 60, "delay": 0.3},
                        {"lon": 79, "lat": 20.0, "t": "~40 LAKH KM²  ·  10+ CRORE LOG", "size": 34, "delay": 1.2}])
NEW["s02"]["source"], NEW["s02"]["source_by"] = "Mughal Empire (c. 1690–1700) — Wikipedia; World History Encyclopedia", "anumaan"
NEW["s03"] = ov("black", "s02", t="Lekin kareeb dedh sau saal baad...")
SEQ.append(("map", ["s02", "s03"]))
# C Delhi fort 1857-58
s = sc_of("s04b"); s["set"] = "fort"; s["target"] = [0.5, 1.0, 5.0]; NEW["s04b"] = s
s = sc_of("s05"); s["set"] = "fort"; s.pop("target", None); NEW["s05"] = s
NEW["s06"] = ov("realdoc", "s05b", **{k: v for k, v in sc_of("s06").items() if k != "type"}, fade_out=False)
NEW["s06b"] = ov("realdoc", "s05b", **{k: v for k, v in sc_of("s06b").items() if k != "type"}, fade_in=False)
SEQ.append(("fort", ["s04", "s04b", "s05", "s05b", "s06", "s06b"]))
# D map Delhi -> Rangoon
m = sc_of("s07")["map"]; NEW["s07"] = GM([70, 10, 102, 34], highlight=m["highlight"], routes=m["routes"], pins=m["pins"],
                                       labels=[{"lon": 87, "lat": 15.0, "t": "2,000+ KM DOOR", "size": 40, "delay": 1.2}])
SEQ.append(("map", ["s07"]))
# E Rangoon cell
NEW["s08"] = {"type": "set3d", "set": "cell", "actors": [A("zafar", 0.6, 3.4, expr="sad")], "objs": [O("grave", -0.8, 3.0, h=0.9)],
              "big": {"t": "KAISE?", "y": 0.16, "at": 0.6}, "target": [0, 0.9, 3.2], "dist": 4.2}
SEQ.append(("cell", ["s07b", "s08"]))
# F court: the big questions
NEW["s09"] = {"type": "set3d", "set": "court", "objs": [O("throne", 0, 9.5, y=0.6, h=1.8)], "target": [0, 1.2, 7.0], "dist": 7.5,
              "stickers": [{"name": "warning", "side": "top_right", "anim": "pop", "h": 0.14, "at": 0.5}],
              "names": [{"t": "Sirf ek jung nahi", "x": 0.04, "y": 0.72, "at": 0.5}]}
NEW["s09b"] = ov("black", "s09", t="Ek kamzori... jo pehle din se maujood thi.")
s = sc_of("s11"); s["set"] = "court"; s["target"] = [0, 1.0, 6.4]; s["dist"] = 4.0
s["objs"] = [O("chest", 0, 6.6, h=0.75), O("kohinoor", 0, 6.6, y=0.75, h=0.9)]; NEW["s11"] = s
SEQ.append(("court", ["s09", "s09b", "s10", "s11", "s12"]))
# G Bengal river
SEQ.append(("river", ["s12b"]))
# H map: 331 years -> Fergana
NEW["s13"] = GM([58, 5, 100, 40], highlight=IND_HL, labels=[{"lon": 78, "lat": 22, "t": "331 SAAL", "size": 80, "delay": 0.3}])
NEW["s13b"] = GM([62, 8, 96, 38], highlight=IND_HL, labels=[{"lon": 78, "lat": 22, "t": "1526 – 1857", "size": 70, "delay": 0.2}])
NEW["s14"] = ov("black", "s13b", t="Ek gyarah saal ka ladka...")
m = sc_of("s15")["map"]; NEW["s15"] = GM([62, 33, 80, 45], highlight={"UZB": "#3f8a6a", "IND": "#8a6a3a"}, pins=m["pins"],
                                       labels=[{"lon": 66, "lat": 43.5, "t": "AAJ KA UZBEKISTAN", "size": 34, "delay": 1.0}])
SEQ.append(("map", ["s13", "s13b", "s14", "s15"]))
# I Akhsi cliff
SEQ.append(("cliff", ["s16", "s16b"]))
# J Fergana palace
NEW["s20"] = ov("map", "s19", **minimap("s20"))
SEQ.append(("palace", ["s17", "s18", "s18b", "s19", "s20"]))
# K tent
SEQ.append(("tent", ["s20b"]))
# L Samarkand fort
s = sc_of("s22"); s["set"] = "fort"; NEW["s22"] = s
NEW["s23b"] = ov("map", "s23", **minimap("s23b"))
SEQ.append(("fort", ["s21", "s22", "s22b", "s23", "s23b"]))
# M wandering plains
NEW["s27"] = ov("map", "s26", **minimap("s27"))
SEQ.append(("plain", ["s24", "s25", "s26", "s27"]))
# N Kabul fort
s = sc_of("s28b"); s["set"] = "fort"; NEW["s28b"] = s
s = sc_of("s29"); s["set"] = "fort"; s.pop("target", None); NEW["s29"] = s
SEQ.append(("fort", ["s28", "s28b", "s29"]))
# O map Kabul -> Hindustan
m = sc_of("s29b")["map"]; NEW["s29b"] = GM([62, 24, 82, 38], highlight=m["highlight"], routes=m["routes"], labels=m["labels"], pins=m["pins"])
SEQ.append(("map", ["s29b"]))
# P Delhi court of Ibrahim Lodi
SEQ.append(("court", ["s30", "s31"]))
# Q Lahore study
NEW["s32b"] = ov("map", "s32", **minimap("s32b"))
SEQ.append(("study", ["s32", "s32b"]))
# R court again
s = sc_of("s33b"); s["set"] = "court"; s["target"] = [0, 1.5, 9.0]; s["dist"] = 2.6
s["actors"] = [A("ibrahim", 0, 9.0, y=0.6, h=1.4, expr="laugh", talk=True, pose="cross")]; NEW["s33b"] = s
NEW["s34"] = ov("black", "s33b", t="Babur aaya. Lekin mehmaan bankar nahi.")
SEQ.append(("court", ["s33", "s33b", "s34"]))
# S Panipat
for bid in ("s38", "s39"):
    s = sc_of(bid); s["set"] = "battlefield"; NEW[bid] = s
NEW["s41"] = ov("map", "s40b", **minimap("s41"))
s = sc_of("s45b"); s = {"type": "set3d", "set": "battlefield", "target": [1.0, 0.8, 5.6], "dist": 4.2,
                       "objs": [O("sword", 1.6, 5.8, h=0.5), O("crown", 1.0, 5.6, h=0.4, anim="drop"), O("smoke", -1.5, 8, h=1.4)],
                       "names": s.get("names", [])}
NEW["s45b"] = s
NEW["s46"] = ov("realdoc", "s45b", **{k: v for k, v in sc_of("s46").items() if k != "type"}, fade_out=False)
NEW["s46b"] = ov("realdoc", "s45b", **{k: v for k, v in sc_of("s46b").items() if k != "type"}, fade_in=False)
SEQ.append(("battlefield", ["s35", "s36", "s37", "s37b", "s38", "s39", "s40", "s40b", "s41", "s41b", "s42", "s42b",
                            "s43", "s44", "s44b", "s45", "s45b", "s46", "s46b", "s47"]))
# T court: Mughal saltanat
NEW["s48"] = ov("black", "s47b", t="Dilli jeetna ek baat thi. Use bachana, doosri.")
SEQ.append(("court", ["s47b", "s48"]))
# U Mewar fort
SEQ.append(("fort", ["s49", "s49b"]))

order = [b for _, ids in SEQ for b in ids]
assert order == [b["id"] for b in story["beats"]], "sequence plan must follow the narration order"


# ------------------------------------------------------------------ assemble scenes
def same(a, b, key):
    return a.get(key) == b.get(key) and abs(a.get("x", 0) - b.get("x", 0)) < 0.6 and abs(a.get("z", 0) - b.get("z", 0)) < 0.6


for loc, ids in SEQ:
    scenes, prev = [], None
    for bid in ids:
        spec = NEW.get(bid)
        if spec and "_overlay_of" in spec:
            base = copy.deepcopy(scenes[-1] if scenes else sc_of(spec["_overlay_of"]))
            for k in ("big", "board", "names", "stickers", "bubble", "emph", "swoosh", "popup", "source", "source_by",
                      "days_left", "month_cal", "caption"):
                base.pop(k, None)
            for a in base.get("actors", []) + base.get("objs", []):
                for f in ("exit", "fade_in", "delay", "anim", "enter", "to"):
                    a.pop(f, None)
            base["overlay"] = spec["overlay"]
            base["_cont"] = True
            sc = base
        else:
            sc = copy.deepcopy(spec) if spec else sc_of(bid)
        sc["type"] = "set3d"
        if loc == "map":
            sc["set"] = "map"; sc["global_map"] = True
        else:
            sc["set"] = sc.get("set", loc) if sc.get("set") in (loc,) else loc
        scenes.append(sc)
    # carry actors / props across beats of the same shot (fade instead of popping)
    for i in range(1, len(scenes)):
        cur, pv = scenes[i], scenes[i - 1]
        if cur.get("_cont"):
            continue
        for key, lst in (("who", "actors"), ("prop", "objs")):
            prev_items = [a for a in pv.get(lst, []) if not a.get("exit")]
            cur_items = cur.get(lst, [])
            for a in cur_items:
                if not any(same(a, p, key) for p in prev_items):
                    a.setdefault("fade_in", True)
            for p in prev_items:
                if not any(same(a, p, key) for a in cur_items):
                    q = copy.deepcopy(p)
                    for f in ("fade_in", "delay", "anim", "enter"):
                        q.pop(f, None)
                    if q.get("to") is not None:   # it already walked: start where it ended
                        q["x"], q["z"] = q["to"][0], q["to"][1]
                        q.pop("to")
                    q["exit"] = True
                    cur.setdefault(lst, []).append(q)
    # camera framing keys -> one continuous Catmull-Rom path through the whole location
    F = []
    for sc in scenes:
        if loc == "map" and sc.get("view"):
            F.append(set3d.view_key(sc["view"]))
        elif sc.get("_cont") and F:
            k = list(F[-1]); k[3] *= 0.94; F.append(k)
        else:
            _, _, dflt = set3d.build(sc["set"], sc)
            F.append(set3d.key_of(sc, dflt))
    timing = json.load(open(P + "/audio/timing.json"))["beats"]
    durs = [timing[b]["dur"] for b in ids]
    S = [0.0]
    for dd in durs:
        S.append(S[-1] + dd)
    for i, sc in enumerate(scenes):
        sc["path"] = {"F": F, "S": S, "i": i}
    n = len(F)
    lerp = lambda a, b, t: [x + (y - x) * t for x, y in zip(a, b)]
    K = [None] * (n + 1)
    K[0] = list(F[0]); K[0][3] *= 1.18; K[0][4] *= 1.05
    for j in range(1, n):
        K[j] = lerp(F[j - 1], F[j], 0.7)
    K[n] = list(F[-1]); K[n][3] *= 0.88
    for i, sc in enumerate(scenes):
        k0 = K[i - 1] if i - 1 >= 0 else K[i]
        k3 = K[i + 2] if i + 2 <= n else K[i + 1]
        sc["keys"] = [k0, K[i], K[i + 1], k3]
        sc.pop("cam", None)
        sc.pop("_cont", None)
    for bid, sc in zip(ids, scenes):
        B[bid]["scene"] = sc
        B[bid].pop("transition", None)
    # seamless location change: rise into clouds at the end, dive out of them at the start
    B[ids[0]]["scene"]["enter_clouds"] = ids[0] != order[0]
    B[ids[-1]]["scene"]["exit_clouds"] = ids[-1] != order[-1]
    if ids[0] != order[0]:
        B[ids[0]]["sfx"] = ["whoosh"] + [x for x in B[ids[0]].get("sfx", []) if x != "whoosh"]

story["auto_transitions"] = False
story["music"] = "investigate"
json.dump(story, open(P + "/story.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(story["beats"]), "beats in", len(SEQ), "continuous shots;",
      sum(1 for b in story["beats"] if b["scene"].get("overlay")), "overlays")
