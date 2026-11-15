# Offre site vitrine 290 € — IL4N STUDIO

- `build.py` : génère un site une page (+ mentions légales) depuis un `site.json`. Aucune dépendance externe, aucun cookie.
  `python3 build.py demo/site.json demo/site`
- `demo/` : site de démonstration **fictif** (Mistraline, plombier à Sarrians), marqué « CONCEPT FICTIF », non indexé (`noindex`).
- `demo/marque/` : identité Mistraline — symbole SVG (rafales de mistral → tuyau en cuivre → goutte), police Bricolage Grotesque (licence OFL, fichier inclus), film et image de secours.
- `demo/film/` : film de marque **HyperFrames** (HTML + GSAP → MP4, 8 s en boucle, sans texte, 25 Ko en 720 px).
  Refaire le rendu : `cd demo/film && npx --yes hyperframes@0.9.46 check && npx --yes hyperframes@0.9.46 render -o film.mp4`
  puis `ffmpeg -i film.mp4 -an -vf scale=720:720 -c:v libx264 -pix_fmt yuv420p -crf 26 -movflags +faststart ../marque/film.mp4`.
- `video-prospection/` : vidéo verticale **HyperFrames** de 10 s (1080×1920, 0,9 Mo) pour présenter l'offre 290 € par WhatsApp/SMS
  → `IL4N-site-290-video-10s.mp4`. Contrôle HyperFrames : 0 erreur, aucun texte affiché trop peu de temps.
  Refaire : `cd video-prospection && npx --yes hyperframes@0.9.46 check && npx --yes hyperframes@0.9.46 render -o video.mp4`.
  Musique originale (synthèse locale, aucun droit tiers) : `video-prospection/audio/musique.py` → version `IL4N-site-290-video-10s-musique.mp4`.
  Voix off : texte et consignes dans `video-prospection/audio/TEXTE-VOIX-OFF.md` ; traitement et mix : `python3 video-prospection/audio/voix.py enregistrement.m4a`.
- `apercus/` : captures ordinateur et mobile.
- `prospection/` : fiche des 10 artisans, script d'appel, objections, `suivi.csv` (à remplir avec des chiffres réels).

Nouveau client : copier `demo/site.json`, remplacer **uniquement** par les informations fournies par le client
(retirer `"fictif": true`, remplir SIRET, responsable, hébergeur ; `atouts`, `horaires` et `avis` seulement s'ils viennent du client ; `marque` est facultatif), ajouter des avis seulement s'ils sont réels et sourcés, puis lancer `build.py`.
Mise en ligne : Netlify gratuit (glisser le dossier généré sur app.netlify.com/drop), uniquement après accord du client.
