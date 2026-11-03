---
name: il4n-flyer-pro
description: Création complète de flyers et d'affiches publicitaires IL4N STUDIO (A6, A5, A4, A3, DL, 40×60, formats sur mesure), recto ou recto-verso, pour commerces, restaurants, artisans, événements. À utiliser quand on demande un flyer, un tract, une affiche, un prospectus, une promo imprimée, ou d'améliorer un flyer existant.
---

# IL4N — Flyer & Affiche Pro

## Quand l'utiliser
- « Fais un flyer / une affiche / un tract pour… », « Refais ce flyer », « Version plus pro ».
- Promotion d'un commerce, ouverture, événement, offre, recrutement, service artisan.
- Pas pour : menu complet (→ `il4n-menu-pro`), visuel réseaux sociaux seul (→ `il4n-social-design`).

## Formats de référence (format fini, fond perdu 3 mm par défaut)
| Format | mm | px 300 ppp (fini) |
|---|---|---|
| A6 | 105 × 148 | 1240 × 1748 |
| A5 | 148 × 210 | 1748 × 2480 |
| A4 | 210 × 297 | 2480 × 3508 |
| A3 | 297 × 420 | 3508 × 4961 |
| DL | 99 × 210 | 1169 × 2480 |
| 40×60 cm | 400 × 600 | viser 150 ppp (vu de loin) |
Marge de sécurité : 4 mm (A6/A5), 5 mm (A4), 8–10 mm (A3 et plus).

## Procédure
1. **Projet** : `bash ~/.claude/il4n-studio/tools/new_project.sh "CLIENT" "FLYER-…" fichiers…` puis remplir `SOURCES/BRIEF.md` (textes copiés à l'identique).
2. **Hiérarchie obligatoire** (de la plus visible à la moins visible) :
   1. Message principal (accroche courte, 3–7 mots) ;
   2. Produit/service (visuel fort) ;
   3. Avantage / info commerciale (offre, prix fourni, date fournie) ;
   4. Coordonnées (adresse, téléphone, site, réseaux — seulement celles fournies) ;
   5. Appel à l'action (« Commandez au… », « Réservez », QR code).
   Lecture en 3 secondes : le passant doit comprendre QUOI, QUI, COMMENT agir.
3. **Direction artistique** : palette 3–5 couleurs (une dominante, une d'accent pour l'offre/CTA, neutres), 1–2 familles typo (titre expressif + texte lisible), grille 6 ou 12 colonnes, un seul point focal. Adapter au secteur (snack/street-food : contrasté, énergique ; artisan : sobre, rassurant ; beauté : aéré, élégant ; événement : affiche typographique forte).
4. **Visuel** : photo client en priorité ; sinon image générée SANS texte (Canva `generate-image`, Figma `generate_image`, Adobe Firefly si connecté) ou composition graphique/typographique. Vérifier la résolution (≥ 300 ppp à taille finale ; image de fond A5 ≥ 1800 × 2520 px).
5. **Mise en page** : écrire `SOURCES/flyer_v1.html` à la taille finale + fond perdu en important `~/.claude/il4n-studio/tools/print-base.css` (fonds dans `.bleed`, textes dans `.safe`). Polices : Google Fonts via `<link>` ou polices système ; éviter les polices non incorporables.
6. **Export** : `node ~/.claude/il4n-studio/tools/export.js SOURCES/flyer_v1.html --w 148 --h 210 --unit mm --bleed 3 --dpi 300 --out EXPORTS/CLIENT_flyer_A5_v1 --pdf --png`
7. **Contrôle** : `il4n-print-preflight` puis `il4n-quality-control` (regarder l'aperçu PNG). Corriger → réexporter.
8. **Livraison** : copier les fichiers validés dans `LIVRAISON/` + `LISEZMOI.md`. Recto-verso : un HTML par face, exporter puis fusionner les PDF dans l'ordre recto/verso (pypdf).

## Règles de lisibilité
- Titre A5 ≥ 28 pt ; texte courant ≥ 9 pt (A5), ≥ 10 pt (A4) ; mentions légales ≥ 6 pt.
- Contraste texte/fond ≥ 4.5:1 ; sur photo, voile ou bandeau derrière le texte.
- Maximum ~40 mots hors coordonnées sur un flyer A5 recto.
- Affiche : lisible à 3 m → titre ≥ 5 % de la hauteur.

## Contrôles qualité spécifiques
- Chaque prix/date/offre est présent dans le brief client (sinon le retirer).
- Le CTA et le moyen de contact sont visibles sans chercher.
- Rien d'important dans les 4 mm du bord ; les fonds débordent bien dans le fond perdu.
- QR code ≥ 18 mm, décodé avec `qr.py check`.

## Livrables
- `CLIENT_flyer_A5_v1_print.pdf` — à envoyer à l'imprimeur (fond perdu, traits de coupe non requis par la plupart des imprimeurs en ligne).
- `CLIENT_flyer_A5_v1_HD.png` — présentation client, réseaux, WhatsApp.
- `flyer_v1.html` — source modifiable.
- Statut explicite : **BAT à valider** ou **prêt imprimeur** (après preflight conforme aux exigences de l'imprimeur).

## Erreurs à éviter
Texte dans l'image générée ; trop de messages concurrents ; 4+ polices ; texte sur photo chargée sans voile ; coordonnées en 6 pt ; promos ou prix inventés ; logo étiré ou recoloré ; fond blanc qui s'arrête au bord (pas de fond perdu) ; « -50 % » non fourni par le client.
