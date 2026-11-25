"""Build the Gemini (Neon / any sandbox agent) skill zip.  python tools/build_gemini_skill.py [out.zip]

Layout of the zip (one root folder, like other uploadable skills):
  itihaas-cartoon-studio/SKILL.md            <- gemini/SKILL.md (guided stage workflow)
  itihaas-cartoon-studio/engine/ assets/ examples/ references/
  itihaas-cartoon-studio/references/script-doctor.md, fact-checker.md   <- from agents/ (frontmatter removed)
"""
import os, re, sys, zipfile

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(PLUGIN, "skills", "itihaas-cartoon-studio")
ROOT = "itihaas-cartoon-studio"
SKIP_DIRS = {"__pycache__", ".git"}
SKIP_FILES = {"east-india-company-demo.json", "east-india-company-toon.json"}   # old styles; eic-founding is current


def strip_front(text):
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).lstrip()


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(PLUGIN, "dist", "itihaas-cartoon-studio-gemini.zip"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(PLUGIN, "gemini", "SKILL.md"), f"{ROOT}/SKILL.md")
        n += 1
        for base, dirs, files in os.walk(SKILL):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for f in sorted(files):
                if f == "SKILL.md" and base == SKILL or f in SKIP_FILES or f.endswith(".pyc"):
                    continue
                p = os.path.join(base, f)
                z.write(p, f"{ROOT}/{os.path.relpath(p, SKILL)}")
                n += 1
        for name in ("script-doctor", "fact-checker"):
            body = strip_front(open(os.path.join(PLUGIN, "agents", f"{name}.md"), encoding="utf-8").read())
            title = name.replace("-", " ").title()
            z.writestr(f"{ROOT}/references/{name}.md",
                       f"# {title} checklist\n\nRun this checklist yourself (there are no sub-agents here).\n\n{body}")
            n += 1
    print(f"OK {out}  ({n} files, {os.path.getsize(out) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
