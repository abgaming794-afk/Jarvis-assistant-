"""Search / download public-domain images from Wikimedia Commons.
python3 tools/commons.py search "query"     -> list titles + license
python3 tools/commons.py get "File:..." out.jpg [width]"""
import sys, json, urllib.request, urllib.parse, urllib.error
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "NaatyaStudio/1.0 (history video research)"}
def q(params):
    params.update(format="json")
    import time
    r = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    for k in range(6):
        try:
            return json.load(urllib.request.urlopen(r, timeout=40))
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(15 * (k + 1))
    raise SystemExit("rate limited")
def info(titles, width=1600):
    d = q(dict(action="query", titles="|".join(titles), prop="imageinfo", iiprop="url|extmetadata|size", iiurlwidth=width))
    out = []
    for p in d["query"]["pages"].values():
        ii = (p.get("imageinfo") or [{}])[0]; m = ii.get("extmetadata", {})
        g = lambda k: (m.get(k, {}).get("value") or "")[:90]
        out.append(dict(title=p["title"], url=ii.get("thumburl") or ii.get("url"), w=ii.get("width"), h=ii.get("height"),
                        lic=g("LicenseShortName"), date=g("DateTimeOriginal"), artist=g("Artist")))
    return out
if sys.argv[1] == "search":
    d = q(dict(action="query", list="search", srsearch=sys.argv[2], srnamespace=6, srlimit=int(sys.argv[3]) if len(sys.argv) > 3 else 8))
    for x in info([h["title"] for h in d["query"]["search"]]) if d["query"]["search"] else []:
        print(x["lic"], "|", x["w"], "x", x["h"], "|", x["title"], "|", x["date"])
else:
    x = info([sys.argv[2]], int(sys.argv[4]) if len(sys.argv) > 4 else 1600)[0]
    r = urllib.request.Request(x["url"], headers=UA)
    open(sys.argv[3], "wb").write(urllib.request.urlopen(r, timeout=60).read())
    print("saved", sys.argv[3], x["lic"], x["artist"])
