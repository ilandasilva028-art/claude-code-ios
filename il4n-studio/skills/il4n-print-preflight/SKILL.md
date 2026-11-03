---
name: il4n-print-preflight
description: Vérification technique IL4N STUDIO des fichiers destinés à l'impression (PDF ou images) — format fini, fond perdu, TrimBox/BleedBox, marges de sécurité, résolution effective, polices incorporées, RGB/CMJN, taille minimale du texte, nombre de pages — et production du PDF « prêt imprimeur ». À utiliser avant toute livraison d'un support imprimé ou quand on demande « prépare le fichier pour l'imprimeur ».
---

# IL4N — Print Preflight

## Quand l'utiliser
- Systématiquement avant de livrer un flyer, affiche, menu, carte, dépliant, kakémono.
- « Prépare le fichier pour l'imprimeur », « Est-ce que ce PDF est bon pour l'impression ? », « L'imprimeur refuse le fichier ».

## Procédure
1. **Récupérer les exigences de l'imprimeur** (dans le brief, sur le gabarit ou la page produit fournie) : format fini, fond perdu (souvent 3 mm, parfois 2 ou 5), marge de sécurité, mode colorimétrique (RGB accepté ? CMJN exigé ? profil ICC : Coated FOGRA39/ISO Coated v2, FOGRA51…), PDF/X demandé ?, traits de coupe ou non, une face par fichier ou multi-pages. À défaut : 3 mm de fond perdu, 4–5 mm de sécurité, 300 ppp, PDF RGB haute qualité, sans traits de coupe — et le **dire**.
2. **Lancer le preflight** :
   ```bash
   python3 ~/.claude/il4n-studio/tools/preflight.py EXPORTS/X_print.pdf --trim 148x210 --bleed 3 --safe 4 --min-dpi 300 --min-pt 6 [--pages 2] [--cmyk-required] --report APERCUS/preflight_X.md
   ```
   Code retour : 0 conforme, 1 avertissements, 2 erreurs.
3. **Contrôle visuel des repères** :
   ```bash
   python3 ~/.claude/il4n-studio/tools/preview.py EXPORTS/X_print.pdf --out APERCUS/X_reperes --guides --bleed 3 --safe 4
   ```
   Ouvrir l'image (outil Read) : fonds qui débordent jusqu'au bord extérieur, aucun texte/logo hors du cadre cyan, rien d'essentiel coupé par le trait rouge.
4. **Corriger** (dans le HTML/SVG source) puis réexporter et relancer jusqu'à « CONFORME » (ou avertissements expliqués et acceptables).
5. **CMJN si exigé** : `bash ~/.claude/il4n-studio/tools/cmyk.sh in.pdf out_CMJN.pdf [profil_imprimeur.icc]` (Ghostscript requis), reposer les boîtes avec `pdfboxes.py`, relancer preflight avec `--cmyk-required`. Sans Ghostscript ni Adobe connecté : **ne pas livrer comme CMJN** — expliquer la limite et proposer la conversion par l'imprimeur ou via Acrobat. Alternative : Skill `adobe-for-creativity:adobe-design-to-pdf` si Adobe est connecté.
6. **Rapport** : joindre `preflight_X.md` à la livraison et indiquer clairement le statut.

## Statuts
- **PRÊT IMPRIMEUR** : preflight sans erreur, avertissements traités, exigences de l'imprimeur vérifiées une par une (y compris colorimétrie).
- **BAT / À VALIDER** : tout autre cas (exigences inconnues, RGB alors que CMJN demandé, images < 300 ppp acceptées par le client…).

## Points de contrôle (seuils)
| Point | Seuil |
|---|---|
| Dimensions | format fini + 2 × fond perdu (± 0,6 mm) |
| Zone de sécurité | texte/logos ≥ 4 mm de la coupe (5 mm A4, 8 mm A3+) |
| Images | ≥ 300 ppp effectifs (≥ 150 grand format vu de loin) ; < 150 = erreur |
| Texte | ≥ 6 pt (≥ 6,5 pt carte de visite), filets ≥ 0,25 pt |
| Polices | toutes incorporées |
| Noir texte | noir pur ; aplat noir riche seulement pour grandes surfaces (en CMJN : 40/30/30/100) |
| Couverture d'encre | ≤ 300 % (CMJN) — à vérifier avec Acrobat si disponible, sinon signaler non vérifié |

## Erreurs à éviter
Déclarer « prêt imprimeur » sans connaître les exigences ; confondre format fini et format avec fond perdu ; convertir en CMJN sans profil et le présenter comme calibré ; images web 72 ppp agrandies ; texte collé à la coupe ; traits de coupe ajoutés alors que l'imprimeur les refuse.
