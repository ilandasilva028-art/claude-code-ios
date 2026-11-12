#!/usr/bin/env bash
# Turns a gameplay clip into a vertical 1080x1920 video ready for TikTok / Shorts / Reels.
#
# Usage:
#   montage.sh --in clip.mp4 --out video.mp4 [options]
#
# Options:
#   --start SEC        start of the segment to keep (default 0)
#   --end SEC          end of the segment to keep (default: end of clip)
#   --hook "TEXT"      hook shown at the top for the first 3 seconds
#   --subs file.srt    subtitles burned at the bottom
#   --voice file.mp3   voice-over (game sound is lowered under it)
#   --music file.mp3   background music (low volume, looped)
#   --mute-game        remove the game sound (copyrighted radio music)
#   --speed X          playback speed, e.g. 0.5 = slow motion, 1.5 = faster
set -euo pipefail

IN="" OUT="" START=0 END="" HOOK="" SUBS="" VOICE="" MUSIC="" MUTE=0 SPEED=1
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf

while [ $# -gt 0 ]; do
  case "$1" in
    --in) IN="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    --start) START="$2"; shift 2;;
    --end) END="$2"; shift 2;;
    --hook) HOOK="$2"; shift 2;;
    --subs) SUBS="$2"; shift 2;;
    --voice) VOICE="$2"; shift 2;;
    --music) MUSIC="$2"; shift 2;;
    --mute-game) MUTE=1; shift;;
    --speed) SPEED="$2"; shift 2;;
    *) echo "Option inconnue : $1" >&2; exit 1;;
  esac
done
[ -f "$IN" ] || { echo "Clip introuvable : $IN" >&2; exit 1; }
[ -n "$OUT" ] || { echo "--out manquant" >&2; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
[ -n "$END" ] || END="$DUR"
HAS_AUDIO=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" | head -1)

# Video: blurred full-screen background + sharp gameplay in the middle.
V="[0:v]trim=start=${START}:end=${END},setpts=(PTS-STARTPTS)/${SPEED},split[a][b];"
V+="[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.15[bg];"
V+="[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2"

if [ -n "$HOOK" ]; then
  # Wrap the hook to ~20 characters per line; textfile avoids quoting problems.
  printf '%s' "$HOOK" | fold -s -w 20 | sed 's/ *$//' > "$TMP/hook.txt"
  V+=",drawtext=fontfile=${FONT}:textfile=${TMP}/hook.txt:fontsize=72:fontcolor=white"
  V+=":borderw=6:bordercolor=black:line_spacing=12:x=(w-text_w)/2:y=260:enable='lt(t,3)'"
fi
if [ -n "$SUBS" ]; then
  cp "$SUBS" "$TMP/subs.srt"
  V+=",subtitles=${TMP}/subs.srt:force_style='FontName=DejaVu Sans,Bold=1,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2,MarginV=70'"
fi
V+=",format=yuv420p[v]"

# Audio: game sound (optional) + voice + music, mixed together.
INPUTS=(-i "$IN")
A="" MIX="" N=0 GAMEVOL=1
[ -n "$VOICE" ] && GAMEVOL=0.25
if [ -n "$HAS_AUDIO" ] && [ "$MUTE" = 0 ]; then
  A+="[0:a]atrim=start=${START}:end=${END},asetpts=PTS-STARTPTS,atempo=${SPEED},volume=${GAMEVOL}[g];"
  MIX+="[g]"; N=$((N+1))
fi
idx=1
if [ -n "$VOICE" ]; then
  INPUTS+=(-i "$VOICE"); A+="[${idx}:a]volume=1.4[vo];"; MIX+="[vo]"; N=$((N+1)); idx=$((idx+1))
fi
if [ -n "$MUSIC" ]; then
  INPUTS+=(-stream_loop -1 -i "$MUSIC"); A+="[${idx}:a]volume=0.15[mu];"; MIX+="[mu]"; N=$((N+1))
fi

MAP=(-map "[v]")
if [ "$N" -gt 0 ]; then
  A+="${MIX}amix=inputs=${N}:duration=first:normalize=0[aout]"
  MAP+=(-map "[aout]")
fi

FILTER="$V"
[ -n "$A" ] && FILTER+=";${A}"

ffmpeg -hide_banner -loglevel error -y "${INPUTS[@]}" -filter_complex "$FILTER" "${MAP[@]}" \
  -c:v libx264 -preset medium -crf 21 -r 30 -c:a aac -b:a 160k -shortest -movflags +faststart "$OUT"

echo "OK : $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" | cut -d. -f1) s)"
