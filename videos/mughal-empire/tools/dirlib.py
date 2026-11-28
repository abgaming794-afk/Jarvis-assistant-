"""Helpers for directing the full film (build_full.py). One spec per script line, grouped into shots.
A shot = (location, [spec, ...]). location 'map' = the one global 3D map. A spec is a scene dict plus
optional beat keys: _y (year), _ov (overlay over the running scene), _sfx."""
import os
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POR = P + "/docs/portraits/"
D = P + "/docs/"

A = lambda who, x, z, **k: dict(who=who, x=x, z=z, **k)
O = lambda prop, x, z, **k: dict(prop=prop, x=x, z=z, **k)
MUGHAL_HL = {"IND": "#d9a72b", "PAK": "#d9a72b", "BGD": "#d9a72b", "AFG": "#c99a35"}
NORTH_HL = {"IND": "#d9a72b", "PAK": "#d9a72b"}
NAATYA = {"t": "Naatya roopantaran", "x": 0.80, "y": 0.035, "at": 0.2, "bar": "#8a7a5a", "small": True}

# places (lon, lat)
PL = dict(delhi=(77.2, 28.6), agra=(78.0, 27.2), chittor=(74.6, 24.9), khanwa=(77.5, 27.0), chanderi=(78.1, 24.7),
          ghaghra=(84.2, 25.8), chausa=(83.9, 25.5), kannauj=(79.9, 27.05), kalinjar=(80.5, 25.0), umerkot=(69.7, 25.4),
          qazvin=(50.0, 36.3), kandahar=(65.7, 31.6), kabul=(69.2, 34.5), sirhind=(76.4, 30.6), kalanaur=(75.2, 32.0),
          panipat=(76.97, 29.39), rewari=(76.6, 28.2), ranthambore=(76.5, 26.0), mandu=(75.4, 22.35), ahmedabad=(72.6, 23.0),
          surat=(72.8, 21.2), dhaka=(90.4, 23.8), gaur=(88.1, 24.9), srinagar=(74.8, 34.1), thatta=(67.9, 24.7),
          amber=(75.85, 26.98), haldighati=(73.68, 24.89), fatehpur=(77.66, 27.09), lahore=(74.3, 31.5), burhanpur=(76.2, 21.3),
          balkh=(66.9, 36.8), samugarh=(78.1, 27.1), arakan=(93.2, 20.6), pune=(73.86, 18.52), raigad=(73.44, 18.23),
          bijapur=(75.7, 16.83), golconda=(78.4, 17.38), ahmednagar=(74.74, 19.1), khuldabad=(75.19, 20.01),
          jajau=(77.9, 26.9), hyderabad=(78.47, 17.38), lucknow=(80.9, 26.8), murshidabad=(88.27, 24.18), karnal=(76.99, 29.69),
          mashhad=(59.6, 36.3), isfahan=(51.7, 32.65), plassey=(88.25, 23.8), buxar=(83.98, 25.56), allahabad=(81.85, 25.43),
          meerut=(77.7, 28.98), rangoon=(96.16, 16.8), calcutta=(88.36, 22.57), kashi=(83.0, 25.3), mathura=(77.67, 27.49),
          jodhpur=(73.02, 26.24), kalpi=(79.74, 26.12), bhimber=(74.08, 32.97), khatoli=(76.3, 25.4), sasaram=(84.0, 24.95),
          sindh=(68.4, 25.4), patna=(85.1, 25.6), chandni=(77.23, 28.656), oudh=(82.1, 26.8))


def S(set_, **k):
    return dict(type="set3d", set=set_, **k)


def GM(view, **m):
    extra = {k: m.pop(k) for k in list(m) if k.startswith("_") or k in ("big", "names", "source", "source_by", "chapter_card")}
    d = {"type": "set3d", "set": "map", "global_map": True, "view": view, "map": m}
    d.update(extra)
    return d


def NM(t, at=0.4, bar=None):
    d = {"t": t, "x": 0.04, "y": 0.72, "at": at}
    if bar:
        d["bar"] = bar
    return [d]


def BIG(t, at=0.3, y=0.16, size=None, anim="rise", frm=None):
    d = {"t": t, "at": at, "y": y, "anim": anim}
    if size:
        d["size"] = size
    if frm is not None:
        d["from"] = frm
    return d


def OV_BLACK(t, **k):
    y = k.pop("_y", None)
    d = {"_ov": dict(type="black", t=t, **k)}
    if y:
        d["_y"] = y
    return d


def OV_DOC(img, src, by="Wikimedia Commons · Public domain", crop=None, **k):
    d = dict(type="realdoc", img=img, tone=k.pop("tone", "sepia"), push=k.pop("push", [1.0, 1.25]), yaw=k.pop("yaw", [-6, 4]),
             curl=k.pop("curl", 0.25), focus=k.pop("focus", [0.5, 0.45]), source=src, source_by=by)
    if crop:
        d["crop"] = crop
    y = k.pop("_y", None)
    d.update(k)
    out = {"_ov": d}
    if y:
        out["_y"] = y
    return out


def PIN(place, label, delay=0.2):
    lon, lat = PL[place]
    return {"lon": lon, "lat": lat, "label": label, "delay": delay}


def LBL(place_or_ll, t, size=44, delay=0.3, dlat=-2.2, **k):
    lon, lat = PL[place_or_ll] if isinstance(place_or_ll, str) else place_or_ll
    d = {"lon": lon, "lat": lat + dlat, "t": t, "size": size, "delay": delay}
    d.update(k)
    return d


def ROUTE(a, b, via=None, delay=0.3, time=2.0, color="#ffd166", mover=None):
    r = {"from": list(PL[a]), "to": list(PL[b]), "delay": delay, "time": time, "color": color}
    if via:
        r["via"] = [list(PL[v]) if isinstance(v, str) else list(v) for v in via]
    if mover:
        r["mover"] = mover
    return r


def MED(place, img, crop, label, pin=None, delay=0.3, side="left", lift=None):
    lon, lat = PL[place]
    d = {"lon": lon, "lat": lat, "img": POR + img if not img.startswith("/") else img, "crop": crop, "label": label,
         "delay": delay, "side": side}
    if pin:
        d["pin"] = pin
    if lift:
        d["lift"] = lift
    return d


def view_around(place, w=24, h=16):
    lon, lat = PL[place]
    w, h = max(w, 22), max(h, 14)
    return [lon - w / 2, lat - h / 2, lon + w / 2, lat + h / 2]


IND_VIEW = [60, 5, 100, 40]
NORTH_VIEW = [66, 20, 92, 36]

CAST = {
    "humayun": {"preset": "mughal_emperor", "facial": "beard", "hat_color": "#f2efe6", "color": "#2f6d8a", "accent": "#c9a227", "age": "young"},
    "kamran": {"preset": "nawab", "facial": "mustache", "hat_color": "#3a3a3a", "color": "#6a2a2a", "age": "young"},
    "askari": {"preset": "nawab", "facial": None, "hat_color": "#8a6a3a", "color": "#5a4a6a", "age": "young"},
    "hindal": {"preset": "nawab", "facial": None, "hat_color": "#e9e2d0", "color": "#3a6a5a", "age": "young"},
    "shershah": {"preset": "nawab", "facial": "full_beard", "hat_color": "#2f6d3a", "color": "#3a5a2a", "accent": "#e8c547", "age": "adult"},
    "bhishti": {"preset": "farmer", "hat_color": "#e9e2d0"},
    "hamida": {"preset": "rani", "hat": "veil", "hat_color": "#e9d8c0", "color": "#6a3a5a"},
    "akbar_boy": {"preset": "nawab", "facial": None, "hat_color": "#f3e3b5", "color": "#c9a227", "accent": "#7a1f2b", "age": "young"},
    "akbar": {"preset": "mughal_emperor", "facial": "mustache", "hat_color": "#f3e3b5", "color": "#c9a227", "accent": "#7a1f2b", "age": "adult"},
    "bairam": {"preset": "minister", "facial": "full_beard", "hat_color": "#2a2a2a", "color": "#5a3a2a", "age": "adult"},
    "hemu": {"preset": "maharaja", "hat_color": "#d9a72b", "color": "#8a3f22", "accent": "#e8c547", "facial": "mustache"},
    "maansingh": {"preset": "maharaja", "hat_color": "#f2efe6", "color": "#3a5a8a"},
    "pratap": {"preset": "maharaja", "hat_color": "#e0782f", "color": "#c0322b", "accent": "#e8c547", "facial": "handlebar"},
    "todarmal": {"preset": "minister", "hat_color": "#e0782f", "color": "#f0e2c0", "facial": "mustache"},
    "abulfazl": {"preset": "minister", "hat_color": "#f2efe6", "color": "#2f5d4a", "facial": "full_beard"},
    "scholar1": {"preset": "minister", "hat_color": "#e0782f", "color": "#f0e2c0", "facial": "mustache"},
    "scholar2": {"preset": "monk"},
    "scholar3": {"preset": "company_merchant", "hat": None, "color": "#2a2a33"},
    "elizabeth": {"preset": "queen_elizabeth"},
    "merchant": {"preset": "company_merchant"},
    "salim": {"preset": "nawab", "facial": "mustache", "hat_color": "#7a1f2b", "color": "#3f6d5a", "age": "adult"},
    "jahangir": {"preset": "mughal_emperor", "facial": "mustache", "hat_color": "#e9e2d0", "color": "#3f6d5a", "accent": "#c9a227"},
    "khusrau": {"preset": "nawab", "facial": None, "hat_color": "#e9e2d0", "color": "#6a5a7a", "age": "young"},
    "nurjahan": {"preset": "rani", "hat": "veil", "hat_color": "#f2efe6", "color": "#2f6d8a", "accent": "#e8c547"},
    "roe": {"preset": "company_merchant", "hat": "wide_hat", "color": "#1f1d22", "facial": "goatee"},
    "jamesi": {"preset": "king", "color": "#3a2a5a"},
    "mahabat": {"preset": "minister", "hat_color": "#7a1f2b", "color": "#5a3a2a", "facial": "full_beard", "age": "adult"},
    "shahjahan": {"preset": "mughal_emperor", "facial": "full_beard", "hat_color": "#f3e3b5", "color": "#e8e0c8", "accent": "#c9a227"},
    "shahjahan_old": {"preset": "mughal_emperor", "facial": "full_beard", "hair_color": "#ecebe6", "hat_color": "#f2efe6", "color": "#e8e0c8", "age": "old"},
    "mumtaz": {"preset": "rani", "hat": "veil", "hat_color": "#f2d9e0", "color": "#a3233a"},
    "dara": {"preset": "nawab", "facial": "beard", "hat_color": "#f2efe6", "color": "#2f5d8a", "age": "adult"},
    "shuja": {"preset": "nawab", "facial": "beard", "hat_color": "#8a6a3a", "color": "#6a5a2a", "age": "adult"},
    "murad": {"preset": "nawab", "facial": "mustache", "hat_color": "#c0322b", "color": "#8a2a22", "age": "adult"},
    "aurangzeb": {"preset": "mughal_emperor", "facial": "full_beard", "hat_color": "#f2efe6", "color": "#f2efe6", "accent": "#3f6d5a", "jewel": False},
    "aurangzeb_old": {"preset": "mughal_emperor", "facial": "full_beard", "hair_color": "#ecebe6", "hat_color": "#f2efe6", "color": "#f2efe6", "accent": "#3f6d5a", "jewel": False, "age": "old", "body": "thin"},
    "shivaji": {"preset": "maharaja", "facial": "beard", "hat_color": "#e0782f", "color": "#f0e2c0", "accent": "#c9a227"},
    "shaista": {"preset": "nawab", "facial": "full_beard", "hat_color": "#7a1f2b", "color": "#5a3a6a", "body": "fat", "age": "adult"},
    "sambhaji": {"preset": "maharaja", "facial": "mustache", "hat_color": "#e0782f", "color": "#c0322b", "age": "young"},
    "tarabai": {"preset": "rani", "hat": "veil", "hat_color": "#e0782f", "color": "#3f6d3a"},
    "prince_akbar": {"preset": "nawab", "facial": "mustache", "hat_color": "#e9e2d0", "color": "#8a5a2a", "age": "young"},
    "bahadur1": {"preset": "mughal_emperor", "facial": "full_beard", "hair_color": "#9a9a9a", "hat_color": "#f2efe6", "color": "#7a5a3a", "age": "old"},
    "jahandar": {"preset": "mughal_emperor", "facial": "mustache", "hat_color": "#e8c547", "color": "#a3233a"},
    "farrukh": {"preset": "mughal_emperor", "facial": "beard", "hat_color": "#f2efe6", "color": "#3a6a8a", "age": "young"},
    "sayyid1": {"preset": "minister", "hat_color": "#2a2a2a", "color": "#2a3a2a", "facial": "full_beard", "age": "adult"},
    "sayyid2": {"preset": "minister", "hat_color": "#2a2a2a", "color": "#3a2a2a", "facial": "full_beard", "age": "adult"},
    "hamilton": {"preset": "british_officer", "hat": None, "color": "#2a2a33", "hair": "wig"},
    "muhammadshah": {"preset": "mughal_emperor", "facial": "beard", "hat_color": "#e8c547", "color": "#c0567a", "accent": "#e8c547"},
    "nizam": {"preset": "nawab", "facial": "full_beard", "hat_color": "#f2efe6", "color": "#2a4a3a", "age": "old"},
    "bajirao": {"preset": "maharaja", "facial": "mustache", "hat_color": "#e0782f", "color": "#f0e2c0"},
    "nadir": {"preset": "mughal_emperor", "facial": "full_beard", "hat_color": "#7a1f2b", "color": "#3a2a22", "accent": "#c9a227"},
    "persian": {"preset": "minister", "hat": "helmet", "hat_color": "#7a7f88", "color": "#6a2a2a", "facial": "full_beard", "age": "young"},
    "abdali": {"preset": "nawab", "facial": "full_beard", "hat_color": "#2a2a2a", "color": "#3a5a3a", "age": "adult"},
    "ranjit": {"preset": "maharaja", "facial": "full_beard", "hat_color": "#e8c547", "color": "#e0782f"},
    "clive": {"preset": "british_officer"},
    "siraj": {"preset": "nawab", "facial": "mustache", "hat_color": "#f2efe6", "color": "#2f6d8a", "age": "young"},
    "mirjafar": {"preset": "nawab", "facial": "full_beard", "hair_color": "#9a9a9a", "hat_color": "#7a1f2b", "color": "#5a4a2a", "age": "old"},
    "shahalam": {"preset": "mughal_emperor", "facial": "full_beard", "hair_color": "#ecebe6", "hat_color": "#f2efe6", "color": "#c9a227", "age": "old"},
    "ghulam": {"preset": "nawab", "facial": "full_beard", "hat_color": "#2a2a2a", "color": "#4a2a2a", "age": "young"},
    "zafar_young": {"preset": "mughal_emperor", "hair_color": "#9a9a9a", "facial": "full_beard", "hat_color": "#f2efe6", "color": "#e6dfcc", "age": "old"},
    "sepoy": {"preset": "sepoy"},
    "victoria": {"preset": "queen_elizabeth", "hair": "bun", "hair_color": "#3a2a22", "outfit": "dress", "color": "#2b2b3a"},
    "poet": {"preset": "minister", "hat": "cap", "hat_color": "#f2efe6", "color": "#e6dfcc", "facial": "beard"},
}
