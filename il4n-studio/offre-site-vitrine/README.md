# Offre site vitrine 290 € — IL4N STUDIO

- `build.py` : génère un site une page (+ mentions légales) depuis un `site.json`. Aucune dépendance externe, aucun cookie.
  `python3 build.py demo/site.json demo/site`
- `demo/` : site de démonstration **fictif** (Mistraline, plombier à Sarrians), marqué « CONCEPT FICTIF », non indexé (`noindex`).
- `apercus/` : captures ordinateur et mobile.
- `prospection/` : fiche des 10 artisans, script d'appel, objections, `suivi.csv` (à remplir avec des chiffres réels).

Nouveau client : copier `demo/site.json`, remplacer **uniquement** par les informations fournies par le client
(retirer `"fictif": true`, remplir SIRET, responsable, hébergeur), ajouter des avis seulement s'ils sont réels et sourcés, puis lancer `build.py`.
Mise en ligne : Netlify gratuit (glisser le dossier généré sur app.netlify.com/drop), uniquement après accord du client.
