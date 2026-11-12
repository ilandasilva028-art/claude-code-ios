---
name: gta6
description: Chaîne complète pour la chaîne GTA 6 sans visage. Prend un clip de gameplay Xbox et le transforme tout seul en vidéo verticale prête à poster (accroche, voix IA optionnelle, sous-titres, montage, description, hashtags), déposée dans Google Drive. À utiliser quand l'utilisateur tape /gta6, dit « go », « nouveau clip », « fais-moi une vidéo » ou envoie un clip GTA.
---

# /gta6 : du clip brut à la vidéo prête à poster

Tout s'enchaîne sans demander de validation entre les étapes. On ne pose une question que si un élément bloque vraiment (aucun clip trouvé, fichier illisible). Toutes les réponses à l'utilisateur sont en français, courtes : il lit sur son téléphone.

Règles de la chaîne :
- **Pas de visage, pas d'infos perso.** Ne jamais mentionner de vrai nom, de ville ou de lieu réel.
- **Pas de musique protégée.** Si la radio du jeu est audible, utiliser `--mute-game` ou mettre une voix off par-dessus.
- **Ne jamais publier tout seul.** La vidéo finie va dans Drive, et l'utilisateur publie lui-même.

## Dossiers Google Drive
- `GTA6 clips` : clips bruts envoyés depuis l'appli Xbox.
- `GTA6 à publier` : vidéos finies et descriptions.
- `GTA6 à publier/journal.txt` : une ligne par clip traité (id Drive du clip et nom de la vidéo produite), plus le `voice_id` choisi.

Si un dossier manque, le créer avec `create_file` (mimeType `application/vnd.google-apps.folder`).

## Étape 1 : Récupérer les nouveaux clips
1. `search_files` avec `title contains 'GTA6 clips'` pour trouver le dossier, puis `parentId = '<id>' and mimeType contains 'video/'`.
2. Comparer avec `journal.txt` et ne garder que les clips pas encore traités. S'il n'y en a aucun, répondre « Aucun nouveau clip » et s'arrêter.
3. Télécharger chaque clip avec `download_file_content`, puis décoder le base64 dans le scratchpad (`base64 -d`). Si le fichier est trop gros pour passer, prévenir l'utilisateur : un clip de moins de 30 s, ou exporté en 720p depuis l'appli Xbox, passe mieux.
4. Les clips envoyés directement dans la conversation (fichiers dans `/root/.claude/uploads/`) sont aussi acceptés.

## Étape 2 : Trouver le moment fort
1. `ffprobe` pour la durée.
2. Extraire une image toutes les 1 à 2 s en petit format, assemblées en planche contact :
   `ffmpeg -i clip.mp4 -vf "fps=1,scale=320:-1,tile=5x4" planche.jpg`
3. Regarder la planche et choisir le passage le plus spectaculaire, entre 8 et 30 s (crash, explosion, poursuite, saut, moment drôle). Si l'utilisateur a donné un horodatage (« le moment fort est à 0:42 »), il est prioritaire.
4. Repérer aussi un passage à mettre au ralenti s'il y a un impact.

## Étape 3 : Écrire (avec les skills d'écriture)
Appliquer les principes de `social-media-skills:hook-writer` et `social-media-skills:tiktok-script` :
- **Accroche** : 3 à 8 mots, choc ou question, en majuscules sur le mot clé. Exemples : « Il voulait juste acheter du pain… », « Personne ne connaît ce secret de Vice City ».
- **Voix off**, optionnelle mais conseillée : 2 à 4 phrases, ton complice, au maximum la durée du clip.
- **Sous-titres** : un fichier `.srt`, 2 à 5 mots par ligne, calés sur la voix off. Sans voix off, 2 ou 3 lignes de texte qui racontent l'action.

## Étape 4 : Voix IA (ElevenLabs)
Si l'utilisateur a déjà choisi une voix, réutiliser son `voice_id` (noté dans `journal.txt`). Sinon, utiliser `creative_list_voices` et choisir une voix française masculine, grave et posée, puis la noter.
Générer avec `creative_generate_speech`, attendre avec `creative_get_flow_run_status`, puis télécharger le mp3. **Ne jamais relancer une génération déjà partie** : elle coûte des crédits.
Si ElevenLabs n'est pas disponible, passer cette étape et faire une vidéo « texte à l'écran ».

## Étape 5 : Montage
```bash
.claude/skills/gta6/montage.sh --in clip.mp4 --out gta6_<sujet>_<date>.mp4 \
  --start <s> --end <e> --hook "ACCROCHE" --subs subs.srt --voice voix.mp3 [--mute-game] [--speed 0.5]
```
Pour un ralenti au milieu d'un clip : monter les morceaux séparément (vitesse 1, puis 0.5, puis 1) et les assembler avec `ffmpeg -f concat`.
Vérifier le résultat : extraire 2 ou 3 images et les regarder (texte lisible, rien de coupé, format 1080x1920).

## Étape 6 : Description et hashtags
Appliquer `social-media-skills:caption-writer` et `social-media-skills:hashtag-strategy`. Créer `gta6_<sujet>_<date>.txt` :
```
TITRE (YouTube Shorts) : … (moins de 60 caractères, avec « GTA 6 »)
DESCRIPTION (TikTok/Reels) : 1 phrase drôle ou intrigante + question pour les commentaires
HASHTAGS : #GTA6 #GTAVI #ViceCity #Gaming + 2 à 4 précis (#GTA6Clips #GTA6Fails…), 8 au maximum
MEILLEURE HEURE : entre 18 h et 21 h en semaine, entre 11 h et 14 h le week-end
```

## Étape 7 : Livrer
1. Envoyer la vidéo et le `.txt` dans `GTA6 à publier` avec `create_file`. Pour la vidéo, utiliser une référence de fichier `sha256:<hash>:<chemin absolu>` dans `base64Content`, `contentMimeType: video/mp4` et `disableConversionToGoogleType: true`. Ne jamais coller le base64 à la main.
2. Ajouter une ligne dans `journal.txt`.
3. Répondre en 3 lignes au maximum : nombre de vidéos prêtes, titres, et « Tout est dans ton Drive, dossier GTA6 à publier ».
