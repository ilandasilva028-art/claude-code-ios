#!/usr/bin/env bash
# IL4N STUDIO — conversion d'un PDF RGB en CMJN avec Ghostscript (si l'imprimeur l'exige).
# Usage : bash cmyk.sh entree_print.pdf sortie_print_CMJN.pdf [profil.icc]
# Sans profil ICC fourni par l'imprimeur, la conversion utilise le profil CMJN par défaut de Ghostscript :
# le résultat est techniquement en CMJN mais n'est PAS calibré sur la presse de l'imprimeur → vérifier le BAT.
set -euo pipefail
IN="${1:?PDF source requis}"; OUT="${2:?PDF de sortie requis}"; ICC="${3:-}"
command -v gs >/dev/null || { echo "Ghostscript absent (macOS : brew install ghostscript). Conversion CMJN impossible ici."; exit 3; }
ARGS=(-dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress
      -sColorConversionStrategy=CMYK -sProcessColorModel=DeviceCMYK -dOverrideICC=true)
[ -n "$ICC" ] && ARGS+=(-sOutputICCProfile="$ICC")
gs "${ARGS[@]}" -sOutputFile="$OUT" "$IN"
echo "CMJN : $OUT — relancer preflight.py avec --cmyk-required. Les TrimBox/BleedBox doivent être reposées :"
echo "python3 $(dirname "$0")/pdfboxes.py \"$OUT\" <largeur_mm> <hauteur_mm> <fond_perdu_mm>"
