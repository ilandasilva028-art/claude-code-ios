# IL4N STUDIO — Département graphique pour Claude Code

Agent **IL4N — Directeur Artistique** + 7 Skills + boîte à outils de production (HTML → PDF imprimeur / PNG, preflight, QR codes).

## Installation sur le Mac (une seule fois)

Prérequis : Python 3 et Node.js (`brew install node`). Optionnel : Ghostscript pour la conversion CMJN (`brew install ghostscript`).

```bash
git clone -b claude/il4n-directeur-artistique https://github.com/ilandasilva028-art/claude-code-ios.git ~/il4n-install
bash ~/il4n-install/il4n-studio/install.sh
```

Le script :
- copie l'agent dans `~/.claude/agents/il4n-directeur-artistique.md` ;
- copie les Skills dans `~/.claude/skills/il4n-*/SKILL.md` ;
- copie les outils dans `~/.claude/il4n-studio/tools/` ;
- crée `~/IL4N-STUDIO/CLIENTS/` (modifiable via la variable `IL4N_STUDIO_ROOT`) ;
- installe les dépendances (pillow, pypdf, pymupdf, qrcode, opencv, Playwright + Chromium) ;
- lance un diagnostic (`doctor.py`).

Il ne modifie aucun autre agent ni Skill. Une ancienne version IL4N éventuelle est sauvegardée avant mise à jour.

Mise à jour : `cd ~/il4n-install && git pull && bash il4n-studio/install.sh`

## Utilisation

Redémarrer Claude Code, puis dans n'importe quel projet :

- **Automatique** : « Fais un flyer A5 pour ce restaurant » + fichiers joints → Claude délègue à l'agent.
- **Explicite** : « Utilise l'agent il4n-directeur-artistique pour… » ou `@il4n-directeur-artistique …`
- **Skill seul** : `/il4n-flyer-pro`, `/il4n-menu-pro`, `/il4n-business-card`, `/il4n-social-design`, `/il4n-brand-identity`, `/il4n-print-preflight`, `/il4n-quality-control`
- Vérifier l'installation : `/agents` et `python3 ~/.claude/il4n-studio/tools/doctor.py`

Chaque commande est rangée dans `~/IL4N-STUDIO/CLIENTS/CLIENT/PROJET/{SOURCES,EXPORTS,APERCUS,LIVRAISON}`.

## Connecteurs graphiques

L'agent utilise Canva, Figma, Adobe, Orshot et les générateurs d'images **s'ils sont connectés dans la session** (il le vérifie par un appel réel). Adobe doit être autorisé dans les réglages des connecteurs claude.ai pour être utilisable.

## Limites connues

- PDF produits en **RGB** (vectoriel, polices incorporées, fond perdu, TrimBox/BleedBox). Conversion **CMJN** via Ghostscript (`tools/cmyk.sh`) ou Acrobat ; sans profil ICC de l'imprimeur, le CMJN n'est pas calibré.
- Couverture d'encre totale non mesurée localement.
- Les originalités juridiques de logos ne sont pas vérifiées (recherche INPI/EUIPO à faire).
