---
name: il4n-social-design
description: Création de visuels réseaux sociaux IL4N STUDIO — posts, carrousels, stories, couvertures, miniatures pour Instagram, Facebook, TikTok, LinkedIn, YouTube, Pinterest, Google Business — aux bonnes dimensions avec zones sûres. À utiliser pour toute publication, annonce, promo ou déclinaison numérique d'un support.
---

# IL4N — Social Design

## Quand l'utiliser
- « Fais un post Insta pour… », « Décline le flyer en story », « Carrousel de 5 slides », « Bannière Facebook / LinkedIn ».
- Réutiliser aussi : `social-media-skills:platform-specs-and-validation` (specs à jour), `canva:resize-for-social-media`, `social-media-skills:carousel-writer` / `caption-writer` (si légende demandée).

## Dimensions (px) et zones sûres
| Usage | Taille | Zone sûre / remarque |
|---|---|---|
| Instagram post portrait (recommandé) | 1080 × 1350 | la grille du profil affiche un recadrage 3:4 central (≈ 1012 px de large) → garder textes et logo à ≥ 70 px des bords gauche/droit |
| Instagram/Facebook carré | 1080 × 1080 | marge 60 px |
| Story / Reel / TikTok | 1080 × 1920 | rien d'important dans les 250 px du haut et 340 px du bas, ni dans les 120 px de droite (boutons) |
| Facebook post paysage | 1200 × 630 | marge 50 px |
| Couverture Facebook page | 1640 × 856 (affichée 820 × 312 desktop) | contenu essentiel au centre 1640 × 624 |
| LinkedIn post | 1200 × 1200 ou 1200 × 627 | marge 60 px |
| Bannière LinkedIn perso | 1584 × 396 | photo de profil masque le bas gauche |
| Miniature YouTube | 1280 × 720 | coin bas droit masqué par la durée |
| Pinterest | 1000 × 1500 | — |
| Google Business post | 1200 × 900 | — |
Vérifier les specs avec le Skill platform-specs si un doute existe (elles évoluent).

## Procédure
1. **Projet** + BRIEF (plateforme(s), objectif : notoriété, promo, recrutement, événement ; textes fournis).
2. **DA** : reprendre l'identité du client (couleurs/typos/logo) ; un message par visuel ; texte ≤ 20 % de la surface idéalement ; accroche lisible sur mobile (≥ 48 px de corps sur 1080 de large ; texte secondaire ≥ 30 px).
3. **Visuel** : photo client ou image générée sans texte ; composition en HTML à la taille exacte (`--unit px`).
4. **Carrousel** : un HTML par slide (ou une page paramétrée), même grille, numérotation, fil visuel qui incite à swiper, dernière slide = CTA.
5. **Export** : `node ~/.claude/il4n-studio/tools/export.js SOURCES/post_v1.html --w 1080 --h 1350 --unit px --out EXPORTS/CLIENT_insta_post_v1 --png` (option `--scale 2` pour un master 2x, puis réduire). JPG qualité 90 si poids > 1 Mo (Pillow).
6. **Contrôle** : `il4n-quality-control` + superposer les zones sûres sur un aperçu (APERCUS/) pour vérifier qu'aucun texte n'est masqué par l'interface.
7. **Canva** : si le client veut éditer lui-même, recréer la composition dans Canva (`generate-design` / `edit-design`), puis `resize-design` pour les déclinaisons ; fournir le lien d'édition.

## Contrôles qualité spécifiques
- Dimensions exactes en pixels (vérifiées avec Pillow).
- Lisible en vignette (réduire l'aperçu à 30 % et regarder).
- Rien dans les zones masquées (stories : haut/bas ; YouTube : bas droit).
- Poids : < 1 Mo pour post, < 4 Mo story statique ; sRGB.
- Aucune promo/date/prix non fourni.

## Livrables
PNG (ou JPG) par format et par slide, nommés `CLIENT_plateforme_format_v1.png`, sources HTML, lien Canva éventuel, proposition de légende si demandée (clairement séparée du visuel).

## Erreurs à éviter
Texte coupé par l'interface ; flyer A5 simplement réduit en post (texte illisible) ; trop de texte ; mauvais ratio (image recadrée par la plateforme) ; export flou (upscale) ; hashtags/emojis inventés comme « offres ».
