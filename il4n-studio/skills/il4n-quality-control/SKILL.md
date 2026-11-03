---
name: il4n-quality-control
description: Contrôle qualité final IL4N STUDIO de toute création avant livraison — orthographe, exactitude des informations client, lisibilité, hiérarchie, alignements, contraste, images, dimensions, QR codes, exports et rangement des dossiers. À utiliser à la fin de chaque production graphique, après chaque correction, et quand on demande de vérifier ou relire un support.
---

# IL4N — Quality Control

## Quand l'utiliser
Toujours, en dernière étape de chaque Skill IL4N, et après chaque correction. Aussi : « Vérifie ce flyer », « Relis la carte avant envoi ».

## Principe
**On contrôle le rendu, pas le code.** Chaque contrôle se fait sur l'aperçu PNG exporté (ouvert avec l'outil Read) et sur le texte extrait du PDF final.

## Procédure
1. **Rendu** : `python3 ~/.claude/il4n-studio/tools/preview.py EXPORTS/X.pdf --out APERCUS/QC_X` (ou utiliser le PNG HD). Regarder l'image entière, puis zoomer sur les zones de texte (recadrage Pillow) si le texte est petit.
2. **Extraction du texte** : `python3 -c "import pymupdf,sys;print(pymupdf.open(sys.argv[1])[0].get_text())" EXPORTS/X_print.pdf` → comparer à `SOURCES/BRIEF.md` mot à mot (noms, prix, téléphone, adresse, horaires, dates, URL, e-mail).
3. **Checklist** (cocher dans `APERCUS/QC_X.md`) :
   - [ ] Orthographe, grammaire, accents, majuscules, espaces insécables avant « : ; ! ? € % » (typographie française), apostrophes typographiques.
   - [ ] Informations identiques à la source ; aucune info inventée (prix, promo, date, horaire, avis, coordonnées).
   - [ ] Concept fictif → mention « CONCEPT FICTIF — IL4N STUDIO » présente ; commande réelle → aucune mention fictive.
   - [ ] Hiérarchie : message principal identifiable en 3 s ; CTA visible.
   - [ ] Lisibilité : corps minimums respectés ; contraste suffisant (≥ 4.5:1 texte courant) ; pas de texte sur zone chargée sans voile.
   - [ ] Alignements sur une grille ; marges régulières ; espacements cohérents ; pas de veuve/orpheline gênante.
   - [ ] Images nettes, non déformées, cohérentes (pas d'artefacts IA : mains, textes parasites, objets fondus) ; logo intact.
   - [ ] Rien de coupé ; rien dans les zones dangereuses (bord, interface réseau social).
   - [ ] Dimensions exactes (Pillow pour PNG, preflight pour PDF) ; résolution adaptée.
   - [ ] QR codes décodés (`qr.py check … --expect …`).
   - [ ] Exports présents, nommés `CLIENT_support_format_vN`, poids raisonnables ; sources modifiables présentes.
   - [ ] Fichiers originaux du client intacts dans `SOURCES/ORIGINAUX/`.
4. **Corriger** chaque point en échec dans la source, réexporter, recontrôler. Ne pas livrer tant qu'un point bloquant subsiste.
5. **Livraison** : copier les fichiers finaux dans `LIVRAISON/` + `LISEZMOI.md` :
   ```
   # Livraison — CLIENT / PROJET — vN — date
   Statut : BAT à valider | Prêt imprimeur (preflight conforme le …)
   - fichier_print.pdf → à envoyer à l'imprimeur (85×55 mm, fond perdu 3 mm, RGB/CMJN)
   - fichier_HD.png → aperçu / réseaux sociaux / WhatsApp
   - source.html → modifications futures
   Points à valider par IL4N STUDIO : …
   ```

## Erreurs à éviter
Valider sur le code sans regarder l'image ; ignorer les avertissements du preflight ; livrer une v2 en écrasant la v1 ; oublier de vérifier l'orthographe des noms propres ; affirmer qu'un QR fonctionne sans l'avoir décodé.
