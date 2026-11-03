---
name: il4n-brand-identity
description: Création de logos et d'identités graphiques IL4N STUDIO — logo vectoriel SVG, variantes (principale, horizontale, monogramme, monochrome, fond clair/fond sombre), palette, typographies, mini charte. À utiliser quand on demande un logo, un rebranding, une identité visuelle, une charte graphique, ou de décliner un logo existant.
---

# IL4N — Brand Identity

## Quand l'utiliser
- « Crée un logo pour… », « Modernise ce logo » (seulement si demandé explicitement), « Fais une charte », « J'ai besoin des versions fond noir / fond blanc ».

## Principes
- Simple, distinctif, mémorisable, cohérent avec l'activité, **lisible à 16 px et à 15 mm de large**.
- Fonctionne en une couleur (noir, blanc) avant d'exister en couleur.
- Ne jamais prétendre que le logo est juridiquement original ou déposable : recommander une recherche d'antériorité (INPI, EUIPO, WIPO Global Brand Database) avant dépôt.
- Ne jamais modifier un logo client existant sans demande explicite.

## Procédure
1. **Projet** + BRIEF : nom exact (orthographe, casse), activité, valeurs, cible, concurrents, contraintes (couleurs imposées, usages : enseigne, broderie, appli).
2. **Recherche & concepts** : 3 pistes distinctes (ex. typographique / symbole / monogramme), chacune avec une justification en 2 lignes. Moodboard optionnel (images générées pour l'ambiance, jamais comme logo final).
3. **Construction vectorielle** : écrire les logos en **SVG à la main** (formes géométriques, chemins, `<text>` converti en chemins si une police doit être figée — sinon indiquer la police utilisée et sa licence). Grille de construction, proportions entières, `viewBox` propre, pas d'image bitmap intégrée.
4. **Variantes** : principale, horizontale, verticale/empilée, icône/monogramme, monochrome noire, monochrome blanche (sur fond sombre), favicon 512 px.
5. **Palette** : 1 couleur principale, 1–2 secondaires, neutres — avec HEX, RGB, et équivalent CMJN **indicatif** (préciser que le CMJN exact dépend du profil de l'imprimeur ; Pantone uniquement si vérifié sur nuancier).
6. **Typographies** : 1 titre + 1 texte, libres de droits (Google Fonts / licence SIL OFL) sauf licence fournie.
7. **Exports** : SVG (source), PDF vectoriel, PNG fond transparent (512, 1024, 2048 px) via `export.js --unit px --transparent` (page HTML sans couleur de fond) ; planche de présentation (logo sur fond clair, sombre, photo, petite taille, mockups enseigne/carte).
8. **Mini charte** (PDF A4 paysage, 3–6 pages) : logo et zone de protection, tailles minimales, variantes, palette, typos, interdits (déformer, recolorer, ombrer…).
9. **Contrôle** : `il4n-quality-control` + test de réduction (16 px, 32 px, 15 mm), test monochrome, test contraste sur fonds.

## Contrôles qualité spécifiques
- SVG valide (s'ouvre dans le navigateur, pas d'éléments hors viewBox, pas de bitmap).
- Lisible en très petit ; pas de détails qui bouchent.
- Nom écrit exactement comme fourni.
- Variantes cohérentes entre elles.

## Livrables
`LOGO/` : SVG, PDF, PNG transparents multi-tailles, favicon ; `CHARTE/` : PDF mini charte ; planche de présentation PNG. Si un outil vectoriel professionnel (Illustrator via Adobe) n'est pas connecté, le dire : les SVG restent ouvrables et éditables dans Illustrator, Figma, Inkscape, Affinity.

## Erreurs à éviter
Logo trop détaillé ou illustratif ; dégradés indispensables à la lecture ; police fantaisie illisible ; copie de codes d'une grande marque ; logo généré en bitmap par IA livré comme « vectoriel » ; promesse d'originalité juridique.
