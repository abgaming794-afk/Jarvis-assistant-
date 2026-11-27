# story.json v2: every beat in a real 3D set (studio/engine/set3d.py), visuals that show what the narrator says,
# a year for the timeline ruler, seamless camera-led transitions. Texts come from SCRIPT.md (voice unchanged).
import json, os, re
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = P + "/docs/"
T = {}
for line in open(P + "/SCRIPT.md", encoding="utf-8"):
    m = re.match(r"- (s\d\db?) (?:\[[^\]]*\])+ (.*)", line.strip())
    if m:
        T[m.group(1)] = m.group(2).strip()
old = {b["id"]: b for b in json.load(open(P + "/story.json", encoding="utf-8"))["beats"]}

EL = lambda v: {"elevenlabs": {"voice_id": v, "model": "eleven_v4"}}
story = {
    "title": "Duniya Ka Sabse Ameer Saltanat Kaise Mita? | Mughal Empire",
    "style": "toon", "res": "360", "fps": 30, "music": "epic", "music_volume": 0.1, "sfx_volume": 0.2,
    "pause": 0.1, "auto_transitions": True,
    "voice": {"engine": "edge", "voice": "hi-IN-MadhurNeural", "rate": "+6%", "pitch": "-6Hz"},
    "speakers": {"N": EL("EppcM8bFS2tfl4Xu0tpj"), "BABUR": EL("n4jGuG5wrMvqWCjMtnMS"), "LODI": EL("7EvySNHBey9ISwbL5Bt5"),
                 "SOLDIER": EL("7b9mYhmnp0y2qSH1FnBL"), "NANI": EL("MaJjkQJkKTqVB1XVQopL")},
    "cast": {
        "babur": {"preset": "mughal_emperor", "facial": "beard", "hat_color": "#efe6cf", "color": "#3f6d5a", "accent": "#c9a227", "age": "young"},
        "babur_boy": {"preset": "nawab", "facial": None, "hat_color": "#efe6cf", "color": "#3f6d5a", "accent": "#c9a227", "age": "young"},
        "umar": {"preset": "mughal_emperor", "color": "#5a3a6a", "hat_color": "#f3e3b5", "age": "adult", "body": "fat"},
        "ibrahim": {"preset": "nawab", "facial": "full_beard", "hat_color": "#7a1f2b", "color": "#8a3f22", "accent": "#e8c547", "age": "adult", "body": "fat"},
        "daulat": {"preset": "minister", "hat_color": "#2f5d8a", "color": "#4a3a6a"},
        "sardar": {"preset": "minister", "hat_color": "#6a2a2a", "color": "#5a4a3a", "age": "adult"},
        "chacha": {"preset": "minister", "hat_color": "#3a3a3a", "color": "#3a4a5a", "age": "adult", "facial": "full_beard"},
        "zafar": {"preset": "mughal_emperor", "hair_color": "#ecebe6", "age": "old", "color": "#e6dfcc", "accent": "#8a7a5a", "jewel": False, "body": "thin", "hat_color": "#f2efe6"},
        "nani": {"preset": "farmer_woman", "skin": "light", "hat_color": "#e9e2d0", "color": "#5a3a5a", "age": "old"},
        "soldier": {"preset": "minister", "hat": "helmet", "hat_color": "#8a8a90", "color": "#6a4a2a", "facial": "mustache", "age": "young"},
        "lodi_soldier": {"preset": "minister", "hat": "helmet", "hat_color": "#6a6a70", "color": "#7a2a22", "facial": "mustache", "age": "young"},
        "ali_quli": {"preset": "minister", "hat": "turban", "hat_color": "#2a2a2a", "color": "#4a5a3a", "facial": "full_beard", "age": "adult"},
        "sanga": {"preset": "maharaja", "hat_color": "#e0782f", "color": "#c0322b", "accent": "#e8c547"},
        "redcoat": {"preset": "british_officer", "hat": "pith_helmet", "hat_color": "#e8e0c8", "hair": "short", "hair_color": "#8a6a4a"},
        "prince1": {"preset": "nawab", "hat_color": "#f2efe6", "color": "#5a6a8a", "facial": "beard", "age": "adult"},
        "prince2": {"preset": "nawab", "hat_color": "#f2efe6", "color": "#6a5a7a", "facial": "mustache", "age": "adult"},
        "grandson": {"preset": "nawab", "hat_color": "#f2efe6", "color": "#7a8a6a", "facial": None, "age": "young"},
        "timur": {"preset": "mughal_emperor", "hat_color": "#3a2a22", "color": "#6a2a2a", "accent": "#c9a227", "facial": "full_beard", "age": "old"},
        "changez": {"preset": "chinese_emperor", "color": "#4a3a2a", "accent": "#c9a227", "hat_color": "#5a4030"},
        "eic": {"preset": "company_merchant"},
    },
    "description": "", "tags": [], "pinned_comment": "", "sources": [], "beats": []}

A = lambda who, x, z, **k: dict(who=who, x=x, z=z, **k)
O = lambda prop, x, z, **k: dict(prop=prop, x=x, z=z, **k)
SRC_M = "Maddison, The World Economy: A Millennial Perspective (OECD, 2001)"
NAATYA = {"t": "NAATYA ROOPANTARAN", "x": 0.80, "y": 0.035, "at": 0.2, "bar": "#8a7a5a", "small": True}


def S(set_, cam, **k):
    d = {"type": "set3d", "set": set_, "cam": cam}
    d.update(k)
    return d


def M(view, cam="dolly_in", **mk):
    """3D tilted map."""
    return {"type": "set3d", "set": "map", "cam": cam, "map_pad": 1.6, "map": dict(view=view, **mk)}


SC, EXTRA = {}, {}
Y = {}
# ------------------------------------------------------------- cold open
SC["s01"] = S("court", "push", objs=[O("peacock_throne", 0, 9.3, y=0.6, h=1.9), O("chest", -2.4, 6.0, h=0.7), O("gold_bars", 2.4, 6.0, h=0.5),
              O("coins", -1.0, 4.8, h=0.4), O("chest", 3.4, 7.6, h=0.7), O("coins", 1.2, 4.6, h=0.4)],
              big={"t": "1/4 DUNIYA KI DAULAT", "y": 0.16}, stickers=[{"name": "coin", "anim": "rain", "h": 0.07, "at": 0.3}])
EXTRA["s01"] = {"sfx": ["cash"], "chapter": "Duniya ki 1/4 daulat"}
SC["s01b"] = {"type": "chart", "bars": [{"label": "HINDUSTAN", "value": 24.4, "text": "24.4%", "color": "#d9a72b"},
                                        {"label": "CHINA", "value": 22.3, "text": "22.3%", "color": "#c0322b"},
                                        {"label": "W. EUROPE", "value": 22.5, "text": "22.5%", "color": "#3a5f8a"}],
              "source": SRC_M + " · saal 1700", "source_by": "anumaan · duniya ki GDP mein hissa"}
SC["s02"] = M([60, 5, 100, 40], "dolly_in", highlight={"IND": "#d9a72b", "PAK": "#d9a72b", "BGD": "#d9a72b", "AFG": "#c99a35"},
              labels=[{"lon": 78, "lat": 22, "t": "MUGHAL HINDUSTAN", "size": 60, "color": "#ffffff", "delay": 0.3},
                      {"lon": 78, "lat": 17.5, "t": "~40 LAKH KM²  ·  10+ CRORE LOG", "size": 34, "color": "#ffe9a8", "delay": 1.2}])
SC["s02"]["source"] = "Mughal Empire (c. 1690–1700) — Wikipedia; World History Encyclopedia"
SC["s02"]["source_by"] = "anumaan"
Y.update(s01=1700, s01b=1700, s02=1700)
SC["s03"] = {"type": "black", "t": "लेकिन करीब डेढ़ सौ साल बाद..."}
SC["s04"] = S("fort", "dolly_in", actors=[A("zafar", 0, 4.2, expr="sad", h=1.3), A("redcoat", -1.6, 4.6, face="right"), A("redcoat", 1.6, 4.6, face="left")],
              caption="DELHI, 1858", names=[{"t": "BAHADUR SHAH ZAFAR · 82 SAAL", "x": 0.06, "y": 0.8, "at": 0.6, "bar": "#c9a227"}])
SC["s04b"] = S("plain", "truck_right", target=[1.0, 1.0, 5.5], objs=[O("bullock_cart", -1.6, 5.6, h=1.6, to=[2.6, 5.6], move_time=4.5)],
               actors=[A("zafar", -2.0, 5.55, y=0.45, h=0.95, expr="sad", to=[2.2, 5.55], walk_time=4.5),
                       A("redcoat", -3.4, 4.6, face="right", to=[0.8, 4.6], walk_time=4.5), A("redcoat", -0.4, 6.8, face="right", to=[3.8, 6.8], walk_time=4.5)],
               caption="OCT 1858 · DESH-NIKALA")
Y.update(s04=1858, s04b=1858)
SC["s05"] = S("palace", "truck_left", actors=[A("prince1", -1.4, 4.4, expr="worried", label="MIRZA MUGHAL"),
                                              A("prince2", 0.1, 4.6, expr="worried", label="MIRZA KHIZR SULTAN"),
                                              A("grandson", 1.6, 4.4, expr="sad", h=1.15, label="MIRZA ABU BAKR (POTA)")])
SC["s05b"] = S("fort", "dolly_out", caption="DELHI · 22 SEP 1857",
               actors=[A("prince1", -1.2, 5.0, expr="sad", dim=True), A("prince2", 0, 5.2, expr="sad", dim=True), A("grandson", 1.2, 5.0, expr="sad", dim=True, h=1.15),
                       A("redcoat", -2.6, 3.6, face="right", pose="hold", hold="musket")],
               names=[{"t": "HODSON NE GOLI MAARI", "x": 0.06, "y": 0.8, "at": 0.5, "bar": "#7a1f2b"}],
               source="Bahadur Shah II — Wikipedia", source_by="historical record")
Y.update(s05=1857, s05b=1857)
SC["s06"] = {"type": "realdoc", "img": D + "zafar_1858_tytler.jpg", "tone": "sepia", "push": [1.0, 1.25], "yaw": [-8, 4], "curl": 0.3,
             "focus": [0.5, 0.45], "source": "Bahadur Shah Zafar, May 1858 — Robert Tytler & Charles Shepherd",
             "source_by": "British Library via Wikimedia Commons · Public domain"}
SC["s06b"] = {"type": "realdoc", "img": D + "zafar_1858_tytler.jpg", "tone": "sepia", "crop": [0.35, 0.05, 0.85, 0.75], "push": [1.1, 1.4],
              "yaw": [6, -4], "focus": [0.5, 0.4], "source": "Bahadur Shah Zafar, May 1858 — Robert Tytler & Charles Shepherd",
              "source_by": "British Library via Wikimedia Commons · Public domain"}
SC["s07"] = M([66, 8, 102, 40], "orbit_right", highlight={"IND": "#c0322b", "MMR": "#6a5a8a"},
              routes=[{"from": [77.2, 28.6], "via": [[81.8, 25.4], [88.3, 22.5]], "to": [96.16, 16.8], "delay": 0.3, "time": 2.4, "mover": "ship", "color": "#ffd166"}],
              pins=[{"lon": 77.2, "lat": 28.6, "label": "DELHI", "delay": 0.1}, {"lon": 96.16, "lat": 16.8, "label": "RANGOON", "delay": 2.6}],
              labels=[{"lon": 87, "lat": 15.5, "t": "2,000+ KM DOOR", "size": 40, "color": "#ffffff", "delay": 1.2}])
SC["s07b"] = S("cell", "dolly_in", objs=[O("grave", 0, 3.2, h=0.9)], caption="RANGOON · 7 NOV 1862",
               names=[{"t": "BENISHAAN QABR", "x": 0.06, "y": 0.8, "at": 0.5}], source="Bahadur Shah Zafar — indianculture.gov.in", source_by="Govt. of India")
Y.update(s06=1858, s06b=1858, s07=1858, s07b=1862)
SC["s08"] = {"type": "split", "left": S("court", "dolly_in", objs=[O("peacock_throne", 0, 9.3, y=0.6, h=1.9)], caption="1700"),
             "right": S("cell", "dolly_in", actors=[A("zafar", 0, 3.0, expr="sad")], caption="1858",
                        stickers=[{"name": "question", "side": "top", "anim": "pop", "h": 0.2, "at": 0.8}])}
SC["s09"] = S("battlefield", "orbit_left", objs=[O("army_block", -3, 9, h=1.8), O("army_block", 3, 10, h=1.8, color="#7a2a22"), O("smoke", 0, 8, h=1.6)],
              stickers=[{"name": "warning", "side": "top_right", "anim": "pop", "h": 0.15, "at": 0.5, "label": "SIRF JUNG NAHI"}])
SC["s09b"] = {"type": "black", "t": "एक कमज़ोरी... जो पहले दिन से मौजूद थी."}
SC["s10"] = S("court", "push", target=[0, 1.6, 8.5], dist=5.0, objs=[O("peacock_throne", 0, 9.3, y=0.6, h=2.1, label="TAKHT-E-TAUS")],
              stickers=[{"name": "question", "side": "top_right", "anim": "pop", "pulse": True, "h": 0.16, "at": 0.6}])
SC["s11"] = S("palace", "dolly_in", target=[0, 1.0, 4.0], dist=4.0, objs=[O("kohinoor", 0, 4.4, y=0.75, h=0.9, label="KOH-I-NOOR")],
              stickers=[{"name": "question", "side": "top_left", "anim": "pop", "h": 0.16, "at": 0.4}], emph=[{"x": 0.5, "y": 0.45, "r": 0.16, "at": 0.4}])
SC["s11"]["_pedestal"] = True
SC["s12"] = S("court", "dolly_in", actors=[A("sardar", -1.4, 6.5, expr="smug", face="right"), A("eic", 1.3, 6.3, face="left", expr="happy")],
              objs=[O("farman", 0, 6.4, y=0.6, h=1.0, anim="pop")], big={"t": "FARMAN 1717 · ₹3,000 / SAAL", "y": 0.14, "at": 0.8},
              source="Farrukh Siyar's Farman — Banglapedia", source_by="historical record")
SC["s12b"] = S("river", "truck_right", objs=[O("ship", 2.5, 11, h=2.4, anim="bob"), O("ship", 6.0, 13, h=2.2, anim="bob"), O("spice_sack", -1.2, 4.4, h=0.7, anim="drop"),
                                             O("spice_sack", -0.3, 4.6, h=0.7, anim="drop", color="#d9822b"), O("eic_flag", 2.4, 6, h=1.4)],
               actors=[A("eic", 0.9, 4.8, expr="laugh", pose="cheer")], caption="BENGAL",
               stickers=[{"name": "arrow_down", "side": "top_right", "anim": "pop", "h": 0.14, "at": 0.6, "label": "BINA CHUNGI"}])
SC["s13"] = S("court", "fly", objs=[O("mughal_flag", 0, 9.4, y=0.6, h=1.4)], big={"t": "331 SAAL", "y": 0.16, "at": 0.4})
SC["s13b"] = M([58, 5, 100, 40], "truck_right", highlight={"IND": "#d9a72b", "PAK": "#d9a72b", "BGD": "#d9a72b", "AFG": "#c99a35"},
               labels=[{"lon": 78, "lat": 22, "t": "1526 – 1857", "size": 70, "color": "#ffffff", "delay": 0.2}])
Y.update(s13=1526, s13b=[1526, 1857])
SC["s14"] = {"type": "black", "t": "एक ग्यारह साल का लड़का..."}
# ------------------------------------------------------------- chapter 1 Babur
CA = [56, 22, 86, 46]
SC["s15"] = M(CA, "dolly_in", highlight={"UZB": "#3f8a6a", "IND": "#8a6a3a"}, pins=[{"lon": 72.3, "lat": 40.8, "label": "FERGANA (ANDIJAN)", "delay": 0.4}],
              labels=[{"lon": 63, "lat": 44.0, "t": "AAJ KA UZBEKISTAN", "size": 34, "color": "#ffffff", "delay": 1.0}])
SC["s16"] = S("cliff", "orbit_right", actors=[A("umar", -0.6, 5.0, expr="happy", face="right")],
              objs=[O("dovecote", 1.4, 6.3, y=0.0, h=2.0)], caption="AKHSI QILA · 1494",
              names=[{"t": "UMAR SHAIKH MIRZA · FERGANA KE SHASAK", "x": 0.06, "y": 0.8, "at": 0.4}])
SC["s16b"] = S("cliff", "shake", actors=[A("umar", 1.1, 6.2, expr="shocked", pose="up", shake=True, face="right")],
               objs=[O("dovecote", 1.4, 6.3, h=2.0, anim="fall", delay=0.3), O("pigeon", 1.2, 6.3, y=1.5, h=0.4, anim="rise", delay=0.4),
                     O("pigeon", 2.0, 6.5, y=1.8, h=0.35, anim="rise", delay=0.6)],
               stickers=[{"name": "warning", "side": "top_right", "anim": "pop", "h": 0.14, "at": 0.4, "label": "KHAAI"}],
               source="Baburnama (tr. A. S. Beveridge, 1922)", source_by="Public domain")
SC["s17"] = S("palace", "crane_up", actors=[A("babur_boy", 0, 5.4, h=1.05, expr="worried"), A("sardar", -1.8, 4.4, face="right", pose="bow"),
                                           A("sardar", 1.8, 4.4, face="left", pose="bow")],
              objs=[O("throne", 0, 6.0, h=1.7), O("crown", 0, 5.4, y=1.3, h=0.35, anim="drop", delay=1.0)],
              names=[{"t": "BABUR · 11 SAAL", "x": 0.06, "y": 0.8, "at": 0.5, "bar": "#c9a227"}])
SC["s18"] = S("palace", "push", target=[0, 0.8, 4.5], dist=3.2, actors=[A("babur_boy", 0, 4.6, h=1.05, expr="proud", pose="hips")],
              emph=[{"x": 0.5, "y": 0.3, "r": 0.14, "at": 0.3}])
SC["s18b"] = S("palace", "truck_left", actors=[A("babur_boy", 0.9, 4.4, h=1.05, expr="proud", face="left"),
                                              A("timur", -1.3, 6.0, h=1.5, expr="proud", dim=True, face="right", label="TIMUR · PITA KI TARAF")])
SC["s19"] = S("palace", "truck_right", actors=[A("babur_boy", 0, 4.4, h=1.05, expr="proud"),
                                              A("timur", -2.0, 6.0, h=1.5, expr="proud", dim=True, face="right", label="TIMUR"),
                                              A("changez", 2.0, 6.0, h=1.5, expr="smug", dim=True, face="left", label="CHANGEZ KHAN · MAA KI TARAF")],
              source="Babur — Encyclopaedia Britannica", source_by="britannica.com")
SC["s20"] = M(CA, "dolly_out", highlight={"UZB": "#3f8a6a"}, pins=[{"lon": 72.3, "lat": 40.8, "label": "FERGANA", "delay": 0.2}],
              labels=[{"lon": 64, "lat": 37.5, "t": "CHHOTA SA RAJYA", "size": 40, "color": "#ffffff", "delay": 0.8}])
SC["s20b"] = S("tent", "orbit_left", actors=[A("babur_boy", 0, 4.4, h=1.05, expr="worried"),
                                            A("chacha", -1.8, 5.2, expr="scheming", face="right", pose="cross", label="CHACHA"),
                                            A("chacha", 1.8, 5.2, expr="angry", face="left", pose="fist", label="CHACHA"),
                                            A("sardar", 0.9, 5.7, expr="smug", face="left", label="BHAI KE SAMARTHAK")],
               objs=[O("sword", -1.2, 5.0, y=1.0, h=0.5), O("sword", 1.4, 5.0, y=1.0, h=0.5)])
SC["s21"] = S("fort", "dolly_in", target=[0, 2.0, 9.0], dist=14.0, height=1.5,
              actors=[A("babur", -1.2, 2.0, h=1.35, back=True, face="right")], names=[{"t": "SAMARKAND · TAIMUR KI RAJDHANI", "x": 0.06, "y": 0.8, "at": 0.4}])
SC["s22"] = S("plain", "truck_right", target=[0.5, 1.0, 6],
              objs=[O("horse_rider", -2.5, 5.2, h=1.8, to=[1.2, 5.2], move_time=4.0, anim="march"),
                    O("army_block", -4.2, 7.0, h=1.8, to=[-0.6, 7.0], move_time=4.0, anim="march"),
                    O("flag", -3.2, 6.0, h=1.6, color="#3f6d5a", to=[0.4, 6.0], move_time=4.0)],
              names=[{"t": "1497 · SIRF 14 SAAL KI UMR", "x": 0.06, "y": 0.8, "at": 0.4}])
SC["s22b"] = S("fort", "crane_up", actors=[A("babur", 0, 4.8, expr="laugh", pose="cheer", jump=True), A("soldier", -1.4, 5.0, expr="happy", pose="cheer"),
                                          A("soldier", 1.4, 5.0, expr="happy", pose="cheer")],
               objs=[O("flag", 0, 9.0, y=4.4, h=1.6, color="#3f6d5a", anim="pop")], caption="SAMARKAND · 1497")
SC["s23"] = S("fort", "dolly_in", actors=[A("babur", 0.6, 4.6, expr="shocked", pose="head")],
              days_left={"x": 0.16, "y": 0.14, "w": 0.2, "n": 100, "title": "SAMARKAND"})
SC["s23b"] = M(CA, "push", highlight={"UZB": "#c0322b"}, pins=[{"lon": 72.3, "lat": 40.8, "label": "FERGANA — HAATH SE GAYA", "delay": 0.2}],
               stickers=[{"name": "arrow_down", "side": "top_right", "anim": "drop", "h": 0.16, "at": 0.4}])
Y.update(s15=1494, s16=1494, s16b=1494, s17=1494, s18=1494, s18b=1494, s19=1494, s20=1494, s20b=1495, s21=1496, s22=1497, s22b=1497, s23=1497, s23b=1498)
SC["s24"] = S("plain", "dolly_in", target=[-0.3, 1.0, 5], dist=3.6, mood=0.75,
              actors=[A("babur", -0.3, 5.0, expr="sad", talk=True, gesture=["shrug", "head", "shrug"], face="right"), A("nani", 1.6, 4.0, back=True, face="left")],
              board={"text": "NA SAMARKAND, NA [GHAR]|AB KAHAN JAUN?", "rect": [0.08, 0.16, 0.64, 0.32], "at": 0.2, "time": 2.0}, names=[NAATYA])
SC["s25"] = S("plain", "orbit_right", target=[0.4, 1.0, 5], dist=3.6, mood=0.75,
              actors=[A("nani", 0.4, 5.0, expr="proud", talk=True, gesture=["point", "idle", "fist"], face="left"), A("babur", -1.4, 4.0, back=True, face="right")],
              names=[{"t": "BABUR KI NAANI", "x": 0.06, "y": 0.8, "at": 0.3, "bar": "#a3233a"}, NAATYA])
SC["s26"] = S("plain", "truck_right", target=[1.0, 1.0, 6],
              actors=[A("babur", -2.5, 5.2, expr="sad", to=[2.5, 5.2], walk_time=4.5, face="right"),
                      A("soldier", -3.6, 5.8, expr="worried", to=[1.4, 5.8], walk_time=4.5, face="right")],
              objs=[O("mughal_tent", 3.5, 9, h=1.8)], month_cal={"x": 0.76, "y": 0.1, "w": 0.16, "title": "1501–1504", "icon": "sword", "at": 0.2, "time": 2.4})
SC["s27"] = M(CA, "orbit_left", highlight={"AFG": "#3f8a6a"}, routes=[{"from": [72.3, 40.8], "via": [[68.8, 37.5]], "to": [69.2, 34.5], "delay": 0.3, "time": 1.8, "color": "#ffd166"}],
              pins=[{"lon": 69.2, "lat": 34.5, "label": "KABUL · 1504", "delay": 2.0}])
SC["s28"] = S("fort", "crane_down", target=[0, 1.6, 8], dist=10, actors=[A("babur", 0, 4.0, expr="thinking", pose="chin")],
              names=[{"t": "KABUL · PAHADI, CHHOTA", "x": 0.06, "y": 0.8, "at": 0.4}])
SC["s28b"] = S("tent", "push", target=[0, 1.2, 4.0], dist=3.4, actors=[A("babur", 0, 4.0, expr="thinking", pose="chin")],
               bubble={"from": [0.55, 0.3], "x": 0.75, "y": 0.18, "prop": "crown", "at": 0.3})
SC["s29"] = S("tent", "dolly_in", actors=[A("babur", 0, 5.4, expr="scheming", pose="point", face="right"), A("sardar", -1.8, 5.0, face="right")],
              caption="KABUL · 1519", stickers=[{"name": "arrow_up", "side": "top_right", "anim": "pop", "h": 0.14, "at": 0.6, "label": "PURAB"}])
SC["s29b"] = M([58, 20, 86, 42], "push", highlight={"AFG": "#3f8a6a", "IND": "#d9a72b", "PAK": "#d9a72b"},
               routes=[{"from": [69.2, 34.5], "via": [[72.0, 33.6]], "to": [77.2, 28.6], "delay": 0.2, "time": 1.8, "color": "#ffd166"}],
               labels=[{"lon": 71.8, "lat": 30.0, "t": "SINDHU", "size": 30, "color": "#9fd3ff", "delay": 0.6}], pins=[{"lon": 77.2, "lat": 28.6, "label": "HINDUSTAN", "delay": 1.8}])
Y.update(s24=1501, s25=1501, s26=[1501, 1504], s27=1504, s28=1504, s28b=1504, s29=1519, s29b=1519)
SC["s30"] = S("court", "dolly_in", actors=[A("ibrahim", 0, 9.0, y=0.6, h=1.4, expr="smug"), A("sardar", -2, 5.2, face="right", pose="bow"),
                                           A("daulat", 2.2, 5.6, face="left", expr="scheming")],
              objs=[O("throne", 0, 9.5, y=0.6, h=1.8)], names=[{"t": "SULTAN IBRAHIM LODI · DILLI", "x": 0.06, "y": 0.8, "at": 0.4, "bar": "#7a1f2b"}])
SC["s31"] = S("court", "orbit_left", target=[0, 1.2, 5], dist=5.0, actors=[A("sardar", -1.0, 5.0, expr="angry", face="right", pose="cross"),
                                                                      A("daulat", 0.4, 5.3, expr="angry", face="left", pose="fist"),
                                                                      A("chacha", 1.6, 5.0, expr="scheming", face="left")],
              emph=[{"x": 0.5, "y": 0.3, "r": 0.14, "at": 0.4}], names=[{"t": "NARAAZ AMIR", "x": 0.06, "y": 0.8, "at": 0.4}])
SC["s32"] = S("study", "dolly_in", actors=[A("daulat", 0, 4.0, expr="scheming", pose="give", hold="letter", hold_size=0.16)],
              names=[{"t": "DAULAT KHAN LODI · PUNJAB KE HAKIM", "x": 0.06, "y": 0.8, "at": 0.4}], source="First Battle of Panipat — Wikipedia", source_by="historical record")
SC["s32b"] = M([58, 20, 86, 42], "orbit_right", highlight={"AFG": "#3f8a6a", "IND": "#d9a72b", "PAK": "#d9a72b"},
               routes=[{"from": [74.3, 31.5], "to": [69.2, 34.5], "delay": 0.3, "time": 1.6, "color": "#ffd166"}],
               pins=[{"lon": 74.3, "lat": 31.5, "label": "LAHORE", "delay": 0.1}, {"lon": 69.2, "lat": 34.5, "label": "KABUL", "delay": 1.8}],
               labels=[{"lon": 72, "lat": 35.6, "t": "NYOTA", "size": 44, "color": "#ffffff", "delay": 1.0}])
SC["s33"] = S("court", "push", target=[0, 1.5, 9.0], dist=4.0, actors=[A("ibrahim", 0, 9.0, y=0.6, h=1.4, expr="laugh", talk=True, gesture=["idle", "point", "cross"])],
              objs=[O("throne", 0, 9.5, y=0.6, h=1.8)], board={"text": "KABUL SE KOI AAYEGA?|AUR [DILLI] LE JAYEGA?", "rect": [0.08, 0.16, 0.6, 0.32], "at": 0.2, "time": 2.0},
              names=[NAATYA])
SC["s33b"] = S("palace", "shake", target=[0, 1.3, 4.5], dist=2.4, actors=[A("ibrahim", 0, 4.5, h=1.4, expr="laugh", talk=True, pose="cross")],
               board={"text": "[MAZAAQ] HAI!", "rect": [0.6, 0.16, 0.92, 0.28], "at": 0.05, "time": 0.8}, names=[NAATYA])
Y.update(s30=1524, s31=1524, s32=1524, s32b=1524, s33=1524, s33b=1524)
SC["s34"] = {"type": "black", "t": "बाबर आया. लेकिन मेहमान बनकर नहीं."}
# ------------------------------------------------------------- Panipat
MUGHAL = [O("araba", -3.6, 6.0, h=1.0), O("araba", -1.6, 6.4, h=1.0), O("cannon", -2.6, 5.6, h=0.7), O("flag", -4.4, 7.5, h=1.6, color="#3f6d5a"),
          O("army_block", -3.2, 8.5, h=1.7, color="#3f6d5a")]
LODI = [O("war_elephant", 3.0, 11, h=2.3, face="left"), O("war_elephant", 5.6, 12.5, h=2.3, face="left"), O("war_elephant", 1.0, 13.5, h=2.3, face="left"),
        O("army_block", 4.0, 15, h=2.0, color="#7a2a22"), O("army_block", 7.0, 16, h=2.0, color="#7a2a22"), O("flag", 6.0, 10.5, h=1.6, color="#7a1f2b")]
SC["s35"] = S("battlefield", "fly", objs=MUGHAL + LODI, caption="PANIPAT · 21 APRIL 1526",
              source="First Battle of Panipat — Wikipedia; Britannica", source_by="historical record")
EXTRA["s35"] = {"chapter": "Panipat, 1526", "sfx": ["drum"]}
SC["s36"] = S("battlefield", "truck_left", target=[-2.5, 1.0, 6], dist=6.5,
              actors=[A("babur", -2.0, 4.8, expr="thinking", pose="chin", face="right")], objs=MUGHAL,
              big={"t": "{n} SAINIK", "count": 12000, "y": 0.16}, source="anumaan — itihaskaar", source_by="First Battle of Panipat · Wikipedia")
SC["s37"] = S("battlefield", "truck_right", target=[4.0, 1.2, 10], dist=8.0,
              actors=[A("ibrahim", 3.0, 8.2, expr="smug", pose="cross", face="left")],
              objs=LODI + [O("army_block", 1.5, 15.5, h=2.0, color="#7a2a22"), O("army_block", 9.0, 15.5, h=2.0, color="#7a2a22")],
              big={"t": "{n} SAINIK*", "count": 100000, "y": 0.16}, source="*Baburnama ke mutabik · itihaskaar 40–70 hazaar", source_by="Wikipedia · historyofwar.org")
SC["s37b"] = S("battlefield", "orbit_right", target=[3.5, 1.2, 11], dist=8.0,
               objs=[O("war_elephant", x, z, h=2.3, face="left") for x, z in ((0.5, 9.5), (3.0, 10.0), (5.5, 10.5), (1.8, 12.5), (4.4, 13.0), (7.0, 13.5), (3.2, 15.5), (6.0, 16.0))],
               big={"t": "~1,000 HAATHI", "y": 0.16, "at": 0.4})
SC["s38"] = S("tent", "dolly_in", target=[0.4, 1.0, 4.4], dist=3.6,
              actors=[A("soldier", 0.4, 4.6, expr="shocked", talk=True, gesture=["shrug", "point", "shrug"], face="left"), A("babur", -1.4, 3.4, back=True, face="right")],
              stickers=[{"name": "exclaim", "side": "top_right", "anim": "pop", "h": 0.14, "at": 0.3}], names=[NAATYA])
SC["s39"] = S("tent", "push", target=[-0.2, 1.1, 4.6], dist=3.0,
              actors=[A("babur", -0.2, 4.6, expr="smug", talk=True, gesture=["idle", "point"], face="right")],
              board={"text": "GINTI MAT KARO.|[GAADIYAN] BAANDHO.", "rect": [0.52, 0.16, 0.94, 0.32], "at": 0.1, "time": 1.6}, names=[NAATYA])
SC["s40"] = S("battlefield", "truck_right", target=[0, 1.0, 6], dist=6.0,
              objs=[O("araba", x, 6.0, h=1.1) for x in (-6, -4, -2, 0, 2, 4, 6)] + [O("rope", -1, 5.2, y=0.5, h=0.5)],
              actors=[A("soldier", -3.0, 4.6, pose="hold", face="right"), A("soldier", 1.2, 4.8, pose="hold", face="left")],
              big={"t": "~700 GAADIYAN", "y": 0.16, "at": 0.4}, source="Baburnama (tr. Beveridge, 1922)", source_by="Public domain")
SC["s40b"] = S("battlefield", "orbit_left", target=[0, 0.8, 5.5], dist=5.0,
               objs=[O("araba", x, 7.0, h=1.1) for x in (-4, -2, 0, 2, 4)] + [O("cannon", -2.2, 5.6, h=0.8), O("cannon", 1.6, 5.6, h=0.8),
                                                                               O("matchlock_man", -0.4, 5.2, h=0.8), O("matchlock_man", 3.0, 5.4, h=0.8)],
               names=[{"t": "TOPEIN + TODEDAAR BANDOOKEIN", "x": 0.06, "y": 0.8, "at": 0.6}])
SC["s41"] = M([25, 25, 80, 48], "truck_right", highlight={"TUR": "#3a6a9a", "AFG": "#3f8a6a"},
              routes=[{"from": [32.9, 39.9], "via": [[50, 36]], "to": [69.2, 34.5], "delay": 0.3, "time": 2.0, "color": "#ffd166"}],
              pins=[{"lon": 32.9, "lat": 39.9, "label": "USMANI TURK", "delay": 0.1}, {"lon": 69.2, "lat": 34.5, "label": "BABUR", "delay": 2.2}])
SC["s41b"] = S("battlefield", "dolly_in", target=[0, 1.0, 5], dist=4.5,
               actors=[A("ali_quli", -0.6, 5.0, expr="proud", pose="point", face="right")], objs=[O("cannon", 1.0, 5.2, h=0.9)],
               names=[{"t": "USTAD ALI QULI · TOPKHANA", "x": 0.06, "y": 0.8, "at": 0.3}])
ENEMY = [O("army_block", 0.0, 11.0, h=2.0, color="#7a2a22"), O("army_block", 2.4, 11.5, h=2.0, color="#7a2a22"), O("war_elephant", 1.2, 9.6, h=2.2, face="left")]
SC["s42"] = S("battlefield", "top", target=[1.0, 0, 11.5], dist=6.5, height=11.0,
              objs=ENEMY + [O("horse_rider", -4.5, 8.0, h=1.6, to=[-3.0, 13.5], move_time=3.6, anim="march"),
                            O("horse_rider", 6.5, 8.0, h=1.6, face="left", to=[5.0, 13.5], move_time=3.6, anim="march")])
SC["s42b"] = S("battlefield", "top", target=[1.0, 0, 12], dist=6.5, height=11.0, yaw=10,
               objs=ENEMY + [O("horse_rider", -3.0, 13.5, h=1.6, to=[0.4, 14.2], move_time=2.5, anim="march"),
                             O("horse_rider", 5.0, 13.5, h=1.6, face="left", to=[2.2, 14.2], move_time=2.5, anim="march")],
               big={"t": "TULUGHMA", "y": 0.16, "at": 0.8}, swoosh=[{"x": 0.5, "y": 0.55, "r": 0.3, "a0": 200, "a1": 340, "color": "#3fbf7a", "at": 0.3}])
SC["s43"] = S("battlefield", "shake", target=[0, 0.8, 5], dist=4.0,
              objs=[O("cannon_fire", -1.0, 5.0, h=1.0), O("cannon_fire", 1.4, 5.6, h=1.0), O("smoke", 0, 7, h=1.6, anim="rise")])
SC["s44"] = S("battlefield", "shake", target=[1.5, 1.2, 9], dist=6.0,
              objs=[O("elephant_panic", 0.5, 9.0, h=2.3, face="left", anim="shake"), O("elephant_panic", 3.0, 10.0, h=2.3, face="left", anim="shake"),
                    O("smoke", -1.5, 7.5, h=1.4)])
SC["s44b"] = S("battlefield", "truck_right", target=[2.0, 1.0, 10], dist=7.0,
               objs=[O("war_elephant", 1.0, 9.0, h=2.3, face="right", to=[3.0, 12.5], move_time=3.0),
                     O("army_block", 3.6, 13.5, h=2.0, color="#7a2a22", anim="shake")],
               actors=[A("lodi_soldier", 5.0, 11.5, expr="shocked", pose="up", face="left", shake=True)],
               names=[{"t": "PARAMPARA KE MUTABIK", "x": 0.06, "y": 0.8, "at": 0.4}])
SC["s45"] = S("battlefield", "crane_up", target=[0, 1.0, 5.5], dist=5.5,
              actors=[A("babur", 0, 5.2, expr="proud", pose="fist")], objs=[O("smoke", -2, 8, h=1.6), O("smoke", 2.6, 9, h=1.3), O("sword", 1.6, 5.8, h=0.5)],
              names=[{"t": "IBRAHIM LODI — MAIDAN ME MAARE GAYE", "x": 0.06, "y": 0.8, "at": 0.6, "bar": "#7a1f2b"}], source="Ibrahim Lodi — Wikipedia", source_by="historical record")
SC["s45b"] = S("court", "dolly_in", target=[0, 1.4, 9.0], dist=5.0, objs=[O("throne", 0, 9.5, y=0.6, h=1.8), O("crown", 0, 9.0, y=0.6, h=0.4, anim="drop")],
               names=[{"t": "DILLI SALTANAT · 1206 – 1526", "x": 0.06, "y": 0.8, "at": 0.5, "bar": "#7a1f2b"}])
SC["s46"] = {"type": "realdoc", "img": D + "panipat_baburnama_1598.jpg", "tone": "ink", "push": [1.0, 1.3], "yaw": [6, -4], "curl": 0.25, "focus": [0.5, 0.5],
             "source": "Battle of Panipat, Baburnama, c. 1598 (Persian copy, Akbar's atelier)", "source_by": "Wikimedia Commons · Public domain"}
SC["s46b"] = {"type": "realdoc", "img": D + "panipat_baburnama_1598.jpg", "tone": "ink", "crop": [0.5, 0.15, 0.98, 0.85], "push": [1.15, 1.45], "yaw": [-6, 4],
              "focus": [0.5, 0.5], "source": "Battle of Panipat, Baburnama, c. 1598 (Persian copy, Akbar's atelier)", "source_by": "Wikimedia Commons · Public domain"}
SC["s47"] = S("battlefield", "orbit_right", target=[0, 1.0, 6], dist=6.5,
              actors=[A("babur", 0, 5.4, expr="laugh", pose="cheer", jump=True), A("soldier", -1.5, 5.8, expr="happy", pose="cheer"), A("soldier", 1.5, 5.8, expr="happy", pose="cheer")],
              objs=[O("flag", 0, 7.5, h=1.8, color="#3f6d5a"), O("army_block", -3, 9, h=1.8, color="#3f6d5a")], big={"t": "~12,000 NE GIRAYI SALTANAT", "y": 0.16, "at": 0.6})
SC["s47b"] = S("court", "fly", actors=[A("babur", 0, 9.0, y=0.6, h=1.4, expr="proud"), A("soldier", -2.2, 6, expr="happy", pose="cheer", face="right"),
                                       A("soldier", 2.2, 6, expr="happy", pose="cheer", face="left")],
               objs=[O("throne", 0, 9.5, y=0.6, h=1.8), O("mughal_flag", -3.4, 8.8, h=1.2), O("mughal_flag", 3.4, 8.8, h=1.2)],
               big={"t": "MUGHAL SALTANAT · 1526", "y": 0.84, "at": 0.8})
SC["s48"] = {"type": "black", "t": "दिल्ली जीतना एक बात थी. उसे बचाना, दूसरी."}
SC["s49"] = S("fort", "fly", target=[0, 1.2, 6], actors=[A("sanga", 0, 5.4, expr="angry", pose="fist", dim=True)],
              objs=[O("army_block", -2.6, 7.5, h=1.8, color="#c0322b"), O("army_block", 2.6, 7.5, h=1.8, color="#c0322b"), O("flag", 0, 8.4, h=1.6, color="#e0782f")],
              caption="MEWAR · 1527")
SC["s49b"] = S("fort", "push", target=[0, 1.0, 5.4], dist=3.0, actors=[A("sanga", 0, 5.4, expr="angry", pose="fist")],
               big={"t": "{n} GHAAV?", "count": 80, "y": 0.16, "at": 1.0}, source="parampara (James Tod, Annals of Rajasthan)", source_by="kehte hain")
Y.update({k: 1526 for k in ("s35", "s36", "s37", "s37b", "s38", "s39", "s40", "s40b", "s41", "s41b", "s42", "s42b", "s43", "s44", "s44b", "s45", "s45b", "s46", "s46b", "s47", "s47b")})
Y.update(s49=1527, s49b=1527)

# ------------------------------------------------------------- assemble
for bid, b in old.items():
    nb = {"id": bid, "speaker": b["speaker"], "text": T.get(bid, b["text"]), "scene": SC[bid]}
    for k in ("tags", "sfx", "chapter"):
        if k in b:
            nb[k] = b[k]
    nb.update(EXTRA.get(bid, {}))
    if bid in Y:
        nb["year"] = Y[bid]
    story["beats"].append(nb)
# kohinoor pedestal: a small gold box under it
for b in story["beats"]:
    sc = b["scene"]
    if sc.pop("_pedestal", False):
        sc.setdefault("objs", []).insert(0, {"prop": "chest", "x": 0, "z": 4.45, "h": 0.75})
story["sources"] = json.load(open(P + "/story.json", encoding="utf-8")).get("sources", [])
json.dump(story, open(P + "/story.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
missing = [k for k in old if k not in SC]
print(len(story["beats"]), "beats; missing scenes:", missing)
