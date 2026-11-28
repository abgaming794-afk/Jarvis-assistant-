"""RECORDING_FULL.md — narrator-only sheet for the whole video (demo s01–s49b + s050…)."""
import json, os, re
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
demo = []
for ln in open(P + "/SCRIPT.md", encoding="utf-8"):
    m = re.match(r"- (s\d+b?) ((?:\[[^\]]*\])*) ?(.*)", ln.strip())
    if m and "DEMO SCRIPT" not in ln:
        tags = m.group(2)
        demo.append(dict(id=m.group(1), who="DLG" if "DIALOGUE" in tags else "N", text=m.group(3).strip(), chapter=0 if int(re.sub(r"\D", "", m.group(1))) < 14 else 1))
full = json.load(open(P + "/script_full/lines.json", encoding="utf-8"))
titles = {0: "Cold open", 1: "Babur: Fergana se Panipat"}
for x in full:
    titles.setdefault(x["chapter"], x["chapter_title"])
rows = demo + full
nar = [r for r in rows if r["who"] == "N"]
words = sum(len(r["text"].split()) for r in nar)
out = [f"# Recording sheet — Mughal Empire (poora video) · {len(nar)} narrator lines · ~{words} shabd · ~{words / 155:.0f} min",
       "",
       "Sirf **narrator** ki lines aap bolenge. Characters ke dialogue (grey, `— skip —`) main AI voice se banaunga — aap unhe mat boliye.",
       "",
       "## Kaise record karein",
       "- **Har chapter ki ek alag file**: `ch0.m4a`, `ch1.m4a`, `ch2.m4a` … `ch9.m4a` (ya mp3/wav). Ek file 2–5 min ki hogi.",
       "- **Har line ke baad ~2 second chup.** Usi se main line kaatunga — har line ek scene hai.",
       "- **Galti ho gayi?** 3–4 second ruk kar wahi poori line dobara boliye. Main hamesha *aakhri* wali le lunga.",
       "- ID (s01, s050…) aur `[tags]` bolne nahi hain. `…` par chhota sa pause.",
       "- Shaant kamra, phone munh se ~20 cm, saari recording ek hi jagah aur ek hi awaaz/energy me. Raftaar normal (~150–160 shabd/min) — main zaroorat ho to halka tez kar dunga.",
       "- Bhejna: files is chat me upload kar dijiye, ya repo me `videos/mughal-empire/audio/raw_own/` me push kar dijiye.",
       ""]
cur = None
for r in rows:
    if r["chapter"] != cur:
        cur = r["chapter"]
        out += ["", f"## ch{cur}.m4a — {titles[cur]}", "", "| ID | line |", "|---|---|"]
    if r["who"] == "N":
        out.append(f"| {r['id']} | {r['text']} |")
    else:
        out.append(f"| — | <span style='color:gray'>— skip — ({r['who'].title() if r['who'] != 'DLG' else 'character'}) {r['text']}</span> |")
open(P + "/RECORDING_FULL.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(nar), "narrator lines,", words, "words")
