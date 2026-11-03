#!/usr/bin/env bash
# IL4N STUDIO — crée le dossier d'une commande et y copie (sans les modifier) les fichiers du client.
# Usage : bash new_project.sh "NOM-CLIENT" "NOM-PROJET" [fichiers_client...]
set -euo pipefail
ROOT="${IL4N_STUDIO_ROOT:-$HOME/IL4N-STUDIO}"
slug() { echo "$1" | iconv -f utf-8 -t ascii//TRANSLIT 2>/dev/null | tr '[:lower:]' '[:upper:]' | sed -E 's/[^A-Z0-9]+/-/g; s/^-+|-+$//g'; }
CLIENT="$(slug "${1:?Nom du client requis}")"
PROJET="$(slug "${2:?Nom du projet requis}")"
shift 2
DIR="$ROOT/CLIENTS/$CLIENT/$PROJET"
mkdir -p "$DIR"/{SOURCES/ORIGINAUX,EXPORTS,APERCUS,LIVRAISON}
for f in "$@"; do
  if [ -e "$f" ]; then
    dest="$DIR/SOURCES/ORIGINAUX/$(basename "$f")"
    if [ -e "$dest" ]; then echo "Déjà présent, non écrasé : $dest"; else cp -p "$f" "$dest" && chmod a-w "$dest"; fi
  fi
done
if [ ! -f "$DIR/SOURCES/BRIEF.md" ]; then
cat > "$DIR/SOURCES/BRIEF.md" <<EOF
# Brief — $CLIENT / $PROJET
Date : $(date +%Y-%m-%d)
Statut : commande réelle | concept fictif portfolio

## Besoin
- Type de création :
- Format final / usage (impression, numérique) :
- Imprimeur et ses exigences (fond perdu, CMJN, profil) :
- Public visé :
- Objectif commercial :

## Textes obligatoires (copiés à l'identique depuis le client)
-

## Coordonnées fournies (ne rien inventer)
-

## Éléments fournis (logo, photos)
-

## Informations manquantes
-

## Direction artistique
- Palette :
- Typographies :
- Composition :
- Traitement photo :
EOF
fi
echo "$DIR"
