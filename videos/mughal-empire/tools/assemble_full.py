"""Assemble script_full/*.txt (after the demo beats s01-s49b) into SCRIPT_FULL.md + lines.json.
Line format: 'N| text' narrator, 'D:WHO| text' dialogue, '## n | chapter title | year' chapter marker."""
import json, re, glob, os
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = ["c1b_c2.txt", "c3_c4.txt", "c5_c6.txt", "c7_c9.txt"]
out, chap, n = [], None, 50
for f in files:
    for ln in open(os.path.join(P, "script_full", f), encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("## "):
            num, title, year = [x.strip() for x in ln[3:].split("|")]
            chap = dict(num=int(num), title=title, year=int(year)); continue
        if not ln.strip() or ln.startswith("#"):
            continue
        who, text = ln.split("|", 1)
        who = "N" if who == "N" else who.split(":", 1)[1]
        out.append(dict(id="s%03d" % n, who=who, text=text.strip(), chapter=chap["num"], chapter_title=chap["title"], chap_year=chap["year"]))
        n += 1
json.dump(out, open(os.path.join(P, "script_full", "lines.json"), "w"), ensure_ascii=False, indent=1)
words = sum(len(x["text"].split()) for x in out)
nar = [x for x in out if x["who"] == "N"]
print(len(out), "lines,", len(nar), "narrator,", words, "words, est", round(len(out) * 3.1 / 60, 1), "min (+3.7 demo)")
md = ["# SCRIPT_FULL — s50 onward (demo s01–s49b in SCRIPT.md)\n"]
cur = None
for x in out:
    if x["chapter"] != cur:
        cur = x["chapter"]; md.append("\n## Chapter %d — %s (%d)\n" % (cur, x["chapter_title"], x["chap_year"]))
    md.append("- %s %s%s" % (x["id"], "" if x["who"] == "N" else "[DLG:%s] " % x["who"], x["text"]))
open(os.path.join(P, "SCRIPT_FULL.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
