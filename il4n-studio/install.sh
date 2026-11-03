#!/usr/bin/env bash
# IL4N STUDIO — installe l'agent « IL4N — Directeur Artistique », ses 7 Skills et la boîte à outils
# dans ~/.claude (agent personnel, disponible dans tous les projets Claude Code).
# Usage : bash install.sh            (installe + dépendances)
#         bash install.sh --no-deps  (fichiers seulement)
# Ne touche à aucun autre agent ni Skill : seuls les fichiers il4n-* sont créés/mis à jour
# (l'ancienne version éventuelle est sauvegardée dans ~/.claude/il4n-studio/backup-<date>/).
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
CLAUDE="$HOME/.claude"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$CLAUDE/il4n-studio/backup-$STAMP"
mkdir -p "$CLAUDE/agents" "$CLAUDE/skills" "$CLAUDE/il4n-studio/tools"

backup() { if [ -e "$1" ]; then mkdir -p "$BACKUP"; cp -R "$1" "$BACKUP/"; fi; }

echo "→ Agent"
backup "$CLAUDE/agents/il4n-directeur-artistique.md"
cp "$SRC/agents/il4n-directeur-artistique.md" "$CLAUDE/agents/"

echo "→ Skills"
for d in "$SRC"/skills/il4n-*; do
  name="$(basename "$d")"
  backup "$CLAUDE/skills/$name"
  rm -rf "$CLAUDE/skills/$name"
  cp -R "$d" "$CLAUDE/skills/$name"
  echo "   $name"
done

echo "→ Boîte à outils"
cp "$SRC"/tools/*.{py,sh,js,css} "$CLAUDE/il4n-studio/tools/"
chmod +x "$CLAUDE/il4n-studio/tools/"*.{py,sh,js}

ROOT="${IL4N_STUDIO_ROOT:-$HOME/IL4N-STUDIO}"
mkdir -p "$ROOT/CLIENTS"
echo "→ Dossier studio : $ROOT"

if [ "${1:-}" != "--no-deps" ]; then
  echo "→ Dépendances Python (pillow, pypdf, pymupdf, qrcode, opencv-python-headless, fonttools)"
  python3 -m pip install --user --quiet --upgrade pillow pypdf pymupdf qrcode opencv-python-headless fonttools \
    || python3 -m pip install --user --quiet --break-system-packages pillow pypdf pymupdf qrcode opencv-python-headless fonttools \
    || echo "   ⚠️  pip a échoué : installez ces paquets manuellement."
  if command -v node >/dev/null && command -v npm >/dev/null; then
    echo "→ Playwright + Chromium (rendu HTML → PDF/PNG)"
    (cd "$CLAUDE/il4n-studio/tools" && { [ -f package.json ] || npm init -y >/dev/null; } && npm install --silent playwright && npx --yes playwright install chromium) \
      || echo "   ⚠️  Installation Playwright échouée : voir doctor.py"
  else
    echo "   ⚠️  Node.js absent : installez-le (brew install node) puis relancez ce script."
  fi
  command -v gs >/dev/null || echo "   (option) Ghostscript absent — nécessaire uniquement pour la conversion CMJN : brew install ghostscript"
fi

echo
python3 "$CLAUDE/il4n-studio/tools/doctor.py" || true
[ -d "$BACKUP" ] && echo "Anciennes versions sauvegardées dans $BACKUP"
echo
echo "Installation terminée. Redémarrez Claude Code, puis tapez /agents pour voir « il4n-directeur-artistique »."
