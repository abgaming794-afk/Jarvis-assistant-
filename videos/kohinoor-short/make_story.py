"""Builds story.json for the Koh-i-Noor Short (9:16). Edit lines here, then run."""
import json, os
P = os.path.dirname(os.path.abspath(__file__))
D = lambda f: os.path.join(P, "docs", f)
TREATY = dict(img=D("treaty_lahore_1849_p653.jpg"), crop=[0.04, 0.29, 0.96, 0.66], w=0.94, tone="sepia",
              source="Treaty of Lahore, 29 March 1849 — Papers relating to the Punjab (1849), p.653",
              source_by="Parliamentary Papers · Internet Archive · Public domain")
DISP = dict(img=D("dalhousie_dispatch_1849_p665.jpg"), crop=[0.04, 0.36, 0.96, 0.52], w=0.96, tone="sepia",
            source="Dalhousie's dispatch, 1849 — Papers relating to the Punjab (1849), p.665",
            source_by="Parliamentary Papers · Internet Archive · Public domain")
TCLOSE = dict(TREATY, crop=[0.04, 0.47, 0.96, 0.63], w=1.25)
cast = {"duleep": {"preset": "maharaja", "facial": None},
        "officer": {"preset": "british_officer"},
        "minister": {"preset": "minister"}, "minister2": {"preset": "nawab"}}
B = []
def beat(i, text, scene, **kw):
    B.append(dict(id=f"s{i:02d}", speaker="N", text=text, scene=scene, **kw))

beat(1, "कोहिनूर, तोहफ़ा था… या लूट?",
     {"type": "set", "bg": "black", "cam": "push_fast", "fg": [],
      "props": [{"name": "diamond", "x": .5, "y": .45, "h": .26, "anim": "pop", "delay": .05}],
      "big": {"t": "GIFT ya LOOT?", "y": .2, "size": 120, "at": .15},
      "emph": [{"x": .5, "y": .45, "r": .12, "at": .2}]}, sfx=["boom"], tags="[dramatic]")
beat(2, "जवाब, अंग्रेज़ों के अपने सरकारी काग़ज़ में लिखा है।",
     dict(TREATY, type="realdoc", push=[1.0, 1.15], yaw=[-28, -10], focus=[.5, .5]), transition="zoom_through", sfx=["page"])
beat(3, "लाहौर। उन्तीस मार्च, अठारह सौ उनचास।",
     {"type": "black", "t": "LAHORE · 29 MARCH 1849", "size": 92, "align": "center"}, transition="flash", sfx=["type"])
beat(4, "पंजाब का महाराजा है, दलीप सिंह।",
     {"type": "set", "bg": "mughal_court", "cam": "dolly_in",
      "props": [{"name": "throne", "x": .5, "y": .72, "h": .3, "layer": "back"}],
      "chars": [{"who": "duleep", "x": .5, "h": .3, "y": -.06, "expr": "worried", "face": "right", "label": "DULEEP SINGH"}],
      "caption": "LAHORE, 1849"}, transition="whip_right")
beat(5, "उम्र? सिर्फ़ दस साल।",
     {"type": "set", "bg": "mughal_court", "cam": "punch", "zoom": 1.3, "focus": [.5, .45],
      "chars": [{"who": "duleep", "x": .5, "h": .62, "close": True, "expr": "sad", "face": "right"}],
      "big": {"t": "{n} SAAL", "count": 10, "y": .2, "size": 150, "at": .3, "color": "#f1c232"}}, sfx=["ding"])
beat(6, "और सिख सेना, जंग हार चुकी है।",
     {"type": "map", "view": [66, 23, 80, 39.5], "highlight": {}, "cam": "drift",
      "labels": [{"lon": 72.6, "lat": 30.6, "t": "PUNJAB", "size": 64, "color": "#7a2a1e", "delay": .2}],
      "pins": [{"lon": 74.35, "lat": 31.55, "label": "LAHORE", "delay": .3}, {"lon": 74.08, "lat": 32.57, "label": "GUJRAT · 1849", "delay": 1.0}],
      "stickers": [{"name": "cannon", "x": .3, "y": .3, "h": .1, "anim": "pop", "at": .9}],
      "source": "Second Anglo-Sikh War, 1848–49", "source_by": "Encyclopaedia Britannica"}, transition="zoom_through", sfx=["boom"])
beat(7, "इसलिए उसका दरबार, अंग्रेज़ों की शर्तें मान लेता है।",
     {"type": "set", "bg": "mughal_court", "cam": "truck_left",
      "props": [{"name": "throne", "x": .5, "y": .62, "h": .24, "layer": "back"},
                {"name": "charter", "x": .5, "y": .38, "h": .16, "anim": "drop", "delay": .3, "label": "SHARTEIN"}],
      "chars": [{"who": "duleep", "x": .5, "h": .24, "y": -.16, "expr": "sad", "face": "right"},
                {"who": "minister", "x": .2, "h": .44, "expr": "worried", "face": "right", "pose": "bow"},
                {"who": "minister2", "x": .8, "h": .44, "expr": "sad", "face": "left", "pose": "head"}],
      "names": [{"t": "Council of Regency", "x": .06, "y": .12, "at": .8, "bar": "#c0322b"}]}, transition="whip_left", sfx=["stamp"])
beat(8, "पहली शर्त: पंजाब पर हर दावा ख़त्म।",
     dict(TCLOSE, type="realdoc", push=[1.0, 1.12], yaw=[-8, -2], focus=[.5, .16], x=.5,
          highlights=[{"rect": [0.14, 0.064, 0.99, 0.124], "at": .4, "time": .6}, {"rect": [0.01, 0.164, 0.99, 0.224], "at": .9, "time": .6},
                      {"rect": [0.01, 0.25, 0.42, 0.31], "at": 1.4, "time": .4}]),
     transition="push_left", sfx=["page"])
beat(9, "और तीसरी शर्त, बस एक पत्थर के लिए।",
     dict(TCLOSE, type="realdoc", push=[1.05, 1.18], yaw=[-4, -1], focus=[.45, .72], x=.56,
          highlights=[{"rect": [0.14, 0.689, 0.99, 0.749], "at": .6, "time": .7}]), transition="cut")
beat(10, "कोहिनूर… इंग्लैंड की रानी को सौंपा जाएगा।",
     dict(TCLOSE, type="realdoc", push=[1.18, 1.3], yaw=[-1, 1], focus=[.5, .84], x=.5,
          highlights=[{"rect": [0.14, 0.689, 0.99, 0.749], "at": 0, "time": .01},
                      {"rect": [0.57, 0.776, 0.99, 0.836], "at": .3, "time": .6, "color": "#ff9a8a"},
                      {"rect": [0.01, 0.858, 0.43, 0.918], "at": .9, "time": .6, "color": "#ff9a8a"}],
          big={"t": "SURRENDERED", "y": .16, "size": 110, "at": .5, "color": "#ff5a4a"}),
     transition="cut", sfx=["stamp"])
beat(11, "यानी तोहफ़ा नहीं। जंग हारने के बाद, शर्त लिखकर लिया गया।",
     {"type": "black", "t": "TOHFA NAHI. SHART.", "size": 110, "align": "center"}, transition="flash", sfx=["drum"])
beat(12, "और डलहौज़ी ने ख़ुद लिखा: समर्पण की निशानी… जीत की यादगार।",
     dict(DISP, type="realdoc", push=[1.1, 1.35], yaw=[14, 4], focus=[.5, .5],
          highlights=[{"rect": [0.01, 0.262, 0.30, 0.312], "at": .9, "time": .5},
                      {"rect": [0.73, 0.54, 0.99, 0.585], "at": 2.0, "time": .4},
                      {"rect": [0.01, 0.633, 0.25, 0.678], "at": 2.4, "time": .4}]),
     transition="zoom_through", sfx=["page"])
beat(13, "अठारह सौ पचास में, जहाज़ से ब्रिटेन, रानी विक्टोरिया के पास।",
     {"type": "map", "view": [-22, -40, 88, 60], "highlight": {"GBR": "#c0322b", "IND": "#e9c46a", "PAK": "#e9c46a"}, "cam": "drift",
      "routes": [{"from": [72.8, 18.9], "via": [[58, 12], [45, -10], [18, -36], [-12, 0], [-12, 40]], "to": [-1.1, 50.8], "bend": .08, "delay": .3, "mover": "ship"}],
      "pins": [{"lon": 72.8, "lat": 18.9, "label": "BOMBAY", "delay": .2}, {"lon": -1.1, "lat": 50.8, "label": "3 JULY 1850", "delay": 3.0}],
      "source": "Koh-i-Noor: HMS Medea, 1850", "source_by": "GIA · World History Encyclopedia"}, transition="whip_up", sfx=["whoosh"])
beat(14, "फिर इसे दोबारा कटवाया गया, करीब बयालीस प्रतिशत वज़न घट गया।",
     {"type": "realdoc", "img": D("kohinoor_original_setting_1851.jpg"), "crop": [0.04, 0, 0.96, 0.9], "w": 1.2, "tone": "sepia",
      "push": [1.0, 1.3], "yaw": [-10, -3], "focus": [.5, .3], "curl": False,
      "big": {"t": "186 se 105.6 CT", "y": .22, "size": 104, "at": 1.0, "color": "#f1c232"},
      "source": "The Koh-i-Noor in its original setting (engraving, 1851)", "source_by": "Wikimedia Commons · Public domain · recut 1852"},
     transition="push_left", sfx=["cash"])
beat(15, "आज भी ये, लंदन के टावर में, एक ताज में जड़ा है।",
     {"type": "set", "bg": "fort", "cam": "dolly_in", "fg": [],
      "props": [{"name": "crown", "x": .5, "y": .42, "h": .24, "anim": "drop"}, {"name": "diamond", "x": .5, "y": .42, "h": .07, "anim": "pop", "delay": .8}],
      "caption": "TOWER OF LONDON · AAJ",
      "names": [{"t": "Tohfa ya shart? Comment karo", "x": .12, "y": .18, "at": 1.4, "bar": "#f1c232"}],
      "emph": [{"x": .5, "y": .5, "r": .1, "at": 1.0}]}, transition="whip_right", sfx=["ding"])
beat(16, "उस दस साल के महाराजा का क्या हुआ? अगला पार्ट — सब्सक्राइब करें।",
     {"type": "realdoc", "img": D("duleep_singh_1854.jpg"), "crop": [0, 0, 1, .62], "w": .62, "tone": "color",
      "push": [1.0, 1.2], "yaw": [-14, -4], "focus": [.5, .3], "curl": False,
      "source": "F. X. Winterhalter, Maharaja Duleep Singh, c.1854", "source_by": "Royal Collection · Wikimedia Commons · Public domain"},
     transition="zoom_through", sfx=["riser"], tags="[softly]")

story = {
    "title": "Koh-i-Noor Gift Tha Ya Loot? 1849 Ki Asli Treaty",
    "style": "toon", "aspect": "9:16", "res": "1080", "fps": 30,
    "subs": True, "sub_y": .655, "sub_size": 66,
    "music": "mystery", "music_volume": 0.10, "sfx_volume": 0.2, "pause": 0.06, "auto_transitions": True,
    "voice": {"engine": "edge", "voice": "hi-IN-MadhurNeural", "rate": "+10%", "pitch": "-6Hz"},
    "speakers": {"N": {"elevenlabs": {"voice_id": "EppcM8bFS2tfl4Xu0tpj", "model": "eleven_v3"}}},
    "cast": cast, "beats": B,
    "description": "Koh-i-Noor angrezon ko tohfe me mila tha ya chheena gaya tha? Jawab 1849 ki Treaty of Lahore ki teesri shart me hai — aur Lord Dalhousie ki apni report me.",
    "tags": ["Koh-i-Noor", "Kohinoor", "Duleep Singh", "Treaty of Lahore 1849", "Dalhousie", "history in hindi", "itihaas", "shorts"],
    "pinned_comment": "Aapke hisaab se Koh-i-Noor ko wapas Bharat aana chahiye? Comment me batao.",
    "sources": [
        {"t": "Papers relating to the Punjab, 1847–1849 (Parliamentary Papers, May 1849), pp. 653, 665", "url": "https://archive.org/details/papersrelatingto00grea"},
        {"t": "Winterhalter, Maharaja Duleep Singh, c.1854 (Wikimedia Commons, PD)", "url": "https://commons.wikimedia.org/wiki/File:Painting_of_Maharaja_Duleep_Singh_by_Franz_Xaver_Winterhalter,_circa_1854.jpg"},
        {"t": "The Koh-i-noor in its original setting, 1851 (Wikimedia Commons, PD)", "url": "https://commons.wikimedia.org/wiki/File:THE_KOH-I-NOOR,_OR_MOUNTAIN_OF_LIGHT.jpg"},
        {"t": "Koh-i-Noor — World History Encyclopedia", "url": "https://www.worldhistory.org/Koh-i-Noor/"},
        {"t": "Famous Diamonds: Koh-i-Noor — GIA", "url": "https://4cs.gia.edu/en-us/blog/famous-diamonds-kohinoor/"},
        {"t": "Sikh Wars — Britannica", "url": "https://www.britannica.com/event/Sikh-Wars"}]}
json.dump(story, open(os.path.join(P, "story.json"), "w"), ensure_ascii=False, indent=1)
print(len(B), "beats,", sum(len(b["text"].split()) for b in B), "words")
