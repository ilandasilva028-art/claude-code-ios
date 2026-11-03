---
name: il4n-menu-pro
description: Conception de menus IL4N STUDIO pour restaurants, snacks, food-trucks, pizzerias, kebabs, burgers, cafés, boulangeries — carte papier (A4, A3, set de table, dépliant), menu panneau/écran, menu Instagram. À utiliser dès qu'il faut mettre en page une carte, des formules, des prix de plats, ou corriger/moderniser un menu existant.
---

# IL4N — Menu Pro

## Quand l'utiliser
- « Fais le menu de ce snack », « Refais notre carte », « Menu pour l'écran du comptoir », « Menu A3 pour la vitrine ».
- Toute mise en page contenant une liste de produits avec prix.

## Règle d'or
**Ne jamais créer un plat, un prix, une taille, un supplément, une formule ou une offre absent des documents fournis.** Les données client sont la seule source de vérité. S'il manque un prix : afficher `[PRIX ?]` en rouge sur le BAT et le signaler, jamais deviner.

## Procédure
1. **Projet** : `new_project.sh "CLIENT" "MENU-…" fichiers…`.
2. **Extraction des données** : transcrire TOUT le contenu fourni (photo du menu, PDF, message) dans `SOURCES/menu_data.json` :
   ```json
   {"categories":[{"nom":"Burgers","items":[{"nom":"Classic","description":"…","prix":{"Seul":"7,50 €","Menu":"9,90 €"}}]}],
    "formules":[…],"supplements":[…],"mentions":["Prix nets TTC", "…"]}
   ```
   Recopier les prix au caractère près (virgule, symbole €). Relire la transcription contre la source ligne par ligne et noter dans BRIEF.md les zones illisibles.
3. **Architecture** : ordre logique du parcours client (formules/menus mis en avant → plats signatures → catégories → accompagnements → boissons → desserts → suppléments/allergènes). Zone « hot spot » (haut droite sur une double page, haut centre sur une simple) pour les produits à forte marge ou la formule phare.
4. **Direction artistique** selon le lieu : snack/street-food (contrasté, gros prix, pictos), bistrot (typo serif, ivoire, filets), pizzeria (chaleureux, rouge/vert dosés), café/brunch (pastel, aéré), écran comptoir (fond sombre, très gros caractères).
5. **Mise en page HTML** générée À PARTIR de `menu_data.json` (script ou template qui boucle sur les données → zéro ressaisie). Alignement des prix : colonne de droite alignée ou prix accolé au nom, cohérent partout. Pas de points de conduite interminables.
6. **Lisibilité** : nom de plat ≥ 10 pt (A4), description ≥ 8 pt, prix ≥ 10 pt gras ; panneau/écran : nom ≥ 4 % de la hauteur. Max 7–9 items par catégorie avant de scinder.
7. **Export** : impression → `export.js … --unit mm --bleed 3 --pdf --png` ; écran → `--unit px --w 1920 --h 1080 --png` (ou 1080×1920 vertical).
8. **Contrôle** : `il4n-print-preflight` (si imprimé) + `il4n-quality-control` + **contrôle de concordance** : script Python qui extrait le texte du PDF (`pymupdf`) et vérifie que chaque nom et chaque prix de `menu_data.json` y figure exactement, et qu'aucun prix du PDF n'est absent du JSON. Joindre le résultat au rapport.

## Contrôles qualité spécifiques
- Concordance 100 % noms/prix/tailles avec la source.
- Mentions obligatoires si fournies (prix nets TTC, origine des viandes, allergènes) — ne pas les inventer, mais signaler si elles semblent manquer (obligation légale en France pour l'origine des viandes bovines et l'information allergènes).
- Cohérence du format des prix (« 8,50 € » partout, pas « 8.5€ » ailleurs).
- Photos de plats : uniquement fournies par le client ou clairement d'illustration (jamais présentées comme le plat réel si générées — le préciser au client).

## Livrables
- PDF impression (fond perdu) et/ou PNG écran, PNG HD de présentation, `menu_data.json` + HTML source (permet les mises à jour de prix rapides), rapport de concordance.

## Erreurs à éviter
Prix ou plats inventés ; « Menu enfant » ajouté par habitude ; prix mal alignés ; trop de photos générées qui trompent le client final ; typo fantaisie illisible pour les descriptions ; oubli des suppléments ; menu écran avec texte trop petit pour être lu à 2 m.
