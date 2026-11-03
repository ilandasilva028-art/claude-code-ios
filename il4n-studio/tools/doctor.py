#!/usr/bin/env python3
"""IL4N STUDIO — diagnostic de la boîte à outils graphique locale.
Usage : python3 ~/.claude/il4n-studio/tools/doctor.py
(Les connecteurs MCP — Canva, Adobe, Figma… — se vérifient depuis Claude Code par un appel réel, pas ici.)
"""
import importlib
import os
import shutil
import subprocess
from pathlib import Path

HOME = Path.home()
TOOLS = Path(__file__).resolve().parent
ok_all = True


def line(ok, label, detail=""):
    global ok_all
    ok_all &= ok or label.startswith("(option)")
    print(f"{'✅' if ok else '❌'} {label}" + (f" — {detail}" if detail else ""))


print("== Fichiers IL4N ==")
agent = HOME / ".claude/agents/il4n-directeur-artistique.md"
line(agent.exists(), "Agent", str(agent))
for s in ["il4n-flyer-pro", "il4n-menu-pro", "il4n-business-card", "il4n-social-design",
          "il4n-brand-identity", "il4n-print-preflight", "il4n-quality-control"]:
    p = HOME / ".claude/skills" / s / "SKILL.md"
    line(p.exists(), f"Skill {s}")

print("\n== Python ==")
for mod, pipname in [("PIL", "pillow"), ("pypdf", "pypdf"), ("pymupdf", "pymupdf"), ("qrcode", "qrcode"), ("cv2", "opencv-python-headless")]:
    try:
        m = importlib.import_module(mod)
        line(True, pipname, getattr(m, "__version__", getattr(m, "VersionBind", "")))
    except Exception:
        line(False, pipname, f"pip3 install --user {pipname}")

print("\n== Rendu HTML → PDF/PNG ==")
node = shutil.which("node")
line(bool(node), "Node.js", node or "installer Node.js (https://nodejs.org ou brew install node)")
if node:
    test = "const p=(()=>{try{return require(process.argv[1]+'/node_modules/playwright')}catch(e){return require('playwright')}})();" \
           "p.chromium.launch(process.env.IL4N_CHROMIUM?{executablePath:process.env.IL4N_CHROMIUM}:{}).then(b=>{console.log(b.version());return b.close()})"
    r = subprocess.run([node, "-e", test, str(TOOLS)], capture_output=True, text=True, timeout=60)
    line(r.returncode == 0, "Playwright + Chromium", r.stdout.strip() or r.stderr.strip().splitlines()[-1] if r.stderr else "")

print("\n== Optionnel ==")
line(bool(shutil.which("gs")), "(option) Ghostscript (conversion CMJN)", shutil.which("gs") or "brew install ghostscript")
line(bool(shutil.which("magick") or shutil.which("convert")), "(option) ImageMagick")
root = Path(os.environ.get("IL4N_STUDIO_ROOT", HOME / "IL4N-STUDIO"))
line(root.exists(), "(option) Dossier studio", str(root))

print("\n" + ("Tout est opérationnel." if ok_all else "Des éléments manquent : voir ❌ ci-dessus."))
