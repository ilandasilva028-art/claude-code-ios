---
name: il4n-business-card
description: Création et correction de cartes de visite IL4N STUDIO recto-verso (85 × 55 mm par défaut, aussi 90 × 50, 85 × 54 ISO, carrées), avec logo, coordonnées et QR code, exports conformes aux imprimeurs. À utiliser quand on demande une carte de visite, carte de fidélité, carte de rendez-vous, ou d'améliorer une carte existante.
---

# IL4N — Carte de visite

## Quand l'utiliser
- « Fais une carte de visite pour… », « Améliore cette carte », « Prépare les cartes pour Vistaprint / Helloprint / Exaprint ».
- Cartes de fidélité / rendez-vous (même gabarit, ajouter les cases ou lignes demandées).

## Gabarit par défaut
- Format fini **85 × 55 mm**, fond perdu 3 mm → document 91 × 61 mm.
- Zone de sécurité 4 mm (texte à ≥ 4 mm de la coupe) ; aucun cadre fin collé au bord (la coupe a ±1 mm de tolérance).
- Recto : identité (logo, nom, activité). Verso : coordonnées + QR/CTA. Recto seul si le client le demande.

## Procédure
1. **Projet** + BRIEF : nom, fonction, téléphone, e-mail, adresse, site, réseaux, logo — **uniquement ce qui est fourni**, recopié au caractère près.
2. **Si amélioration d'une carte existante** : copier l'original dans `SOURCES/ORIGINAUX/`, faire un diagnostic écrit (lisibilité, hiérarchie, alignements, contraste, densité, marges, qualité du logo, cohérence typo), puis proposer la nouvelle version en conservant le logo intact.
3. **QR code** (si utile ou demandé) : `python3 ~/.claude/il4n-studio/tools/qr.py make "https://…" --out SOURCES/qr.svg` (contenu fourni par le client uniquement), taille ≥ 18 mm, zone de silence blanche, contraste foncé sur clair.
4. **Mise en page** : un HTML par face (`recto_v1.html`, `verso_v1.html`) avec `print-base.css`, `--w:85mm;--h:55mm;--bleed:3mm;--safe:4mm`. Logo en SVG/PNG haute définition. Typo : nom 11–14 pt, coordonnées 7,5–9 pt, jamais < 6,5 pt ; graisse regular minimum pour les petits corps sur fond foncé.
5. **Export** (chaque face) : `node ~/.claude/il4n-studio/tools/export.js SOURCES/recto_v1.html --w 85 --h 55 --unit mm --bleed 3 --dpi 600 --out EXPORTS/CLIENT_carte_recto_v1 --pdf --png` puis fusion recto+verso en un PDF 2 pages (pypdf), sauf si l'imprimeur demande un fichier par face.
6. **Contrôles** : `il4n-print-preflight` (`--trim 85x55 --bleed 3 --safe 4 --min-pt 6.5 --pages 2`), `qr.py check EXPORTS/…_HD.png --expect "…"`, puis `il4n-quality-control`. Vérifier en aperçu à 100 % ET en réduit (taille réelle à l'écran) : tout doit rester lisible.
7. **Mockup** de présentation (optionnel) : composition HTML des deux faces en légère perspective/ombre sur fond neutre → `APERCUS/`.

## Contrôles qualité spécifiques
- Chaque caractère des coordonnées comparé au brief (téléphone : format `06 12 34 56 78`, e-mail en minuscules, site sans `https://` à l'affichage).
- Logo non déformé (ratio d'origine), non recoloré sans demande.
- Pas de texte blanc fin < 7 pt sur fond foncé ; pas de filet < 0,25 pt.
- QR décodé = URL attendue.
- 2 pages dans le bon ordre (recto puis verso), même orientation ou orientation déclarée.

## Livrables
- `CLIENT_carte_v1_print.pdf` (2 pages, fond perdu) — pour l'imprimeur.
- `…_recto_HD.png`, `…_verso_HD.png` — validation client.
- Mockup PNG (si fait), sources HTML + QR SVG.
- Indiquer les specs utilisées et rappeler de vérifier celles de l'imprimeur choisi (fond perdu, CMJN, papier).

## Erreurs à éviter
Texte à 2 mm du bord ; corps 5 pt ; QR trop petit ou pointant vers une URL inventée ; adresse incomplète « complétée » de mémoire ; cadre périphérique (coupe visible) ; trop d'informations (8 lignes de contact) ; fond perdu oublié.
