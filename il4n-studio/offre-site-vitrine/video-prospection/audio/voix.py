#!/usr/bin/env python3
"""IL4N STUDIO — traite la voix off d'Ilan et produit la vidéo finale (voix + musique).

Usage : python3 voix.py enregistrement.(m4a|mp3|ogg|opus|wav|mp4)

1. Nettoyage : mono 48 kHz, passe-haut, débruitage, anti-sifflantes, égalisation, compression.
2. Découpage : l'enregistrement est coupé aux pauses en 4 phrases ; chaque phrase est placée au début
   de sa scène (accroche, téléphone, prix, logo) et accélérée légèrement si elle déborde (×1,15 au plus).
   Si on ne trouve pas exactement 4 phrases, la voix est posée d'un bloc depuis 0,15 s.
3. Mix : la musique baisse sous la voix (sidechain), normalisation finale à –16 LUFS.
Sorties : ../IL4N-site-290-video-10s-voix.mp4 et voix_traitee.wav (voix seule, calée).
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ICI = Path(__file__).resolve().parent
VIDEO = ICI.parent / "IL4N-site-290-video-10s.mp4"
SORTIE = ICI.parent / "IL4N-site-290-video-10s-voix.mp4"
MUSIQUE = ICI / "musique.wav"
# début de chaque scène et place disponible pour la phrase (secondes)
SCENES = [(0.15, 2.25), (2.55, 3.2), (5.95, 1.65), (7.75, 2.1)]
NETTOYAGE = ("highpass=f=80,afftdn=nf=-28:tn=1,deesser=i=0.4,"
             "equalizer=f=250:t=q:w=1:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=9000:t=h:w=1:g=1.5,"
             "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2")


def ff(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def duree(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def phrases(f):
    """Repère les segments parlés séparés par au moins 0,35 s de silence."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "silencedetect=n=-38dB:d=0.35", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    debuts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    fins = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    total = duree(f)
    segs, cur = [], 0.0
    for d, e in zip(debuts, fins + [total]):
        if d - cur > 0.15:
            segs.append((cur, d))
        cur = e
    if total - cur > 0.15:
        segs.append((cur, total))
    return segs


def main():
    src = Path(sys.argv[1])
    if not MUSIQUE.exists():
        subprocess.run([sys.executable, str(ICI / "musique.py"), str(ICI / "musique_brute.wav")], check=True)
        ff("-i", str(ICI / "musique_brute.wav"), "-af", "loudnorm=I=-16:TP=-1.5", str(MUSIQUE))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        propre = tmp / "propre.wav"
        ff("-i", str(src), "-vn", "-ac", "1", "-ar", "48000", "-af",
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse," + NETTOYAGE, str(propre))
        segs = phrases(propre)
        print(f"Phrases détectées : {len(segs)} → " + ", ".join(f"{b - a:.1f} s" for a, b in segs))
        morceaux = []
        if len(segs) == len(SCENES):
            for i, ((a, b), (debut, place)) in enumerate(zip(segs, SCENES)):
                tempo = min(1.15, max(1.0, (b - a) / place))
                if (b - a) / tempo > place + 0.15:
                    print(f"⚠️  Phrase {i + 1} trop longue ({b - a:.1f} s pour {place:.1f} s) : la redire plus vite.")
                p = tmp / f"p{i}.wav"
                ff("-i", str(propre), "-af", f"atrim={max(0, a - 0.04):.3f}:{b + 0.06:.3f},asetpts=PTS-STARTPTS,atempo={tempo:.3f}", str(p))
                morceaux.append((p, debut))
                print(f"  phrase {i + 1} : {b - a:.2f} s, ×{tempo:.2f}, placée à {debut:.2f} s")
        else:
            d = duree(propre)
            tempo = min(1.15, max(1.0, d / 9.6))
            if d / tempo > 9.75:
                print("⚠️  Voix trop longue même accélérée : réenregistrer plus vite.")
            p = tmp / "bloc.wav"
            ff("-i", str(propre), "-af", f"atempo={tempo:.3f}", str(p))
            morceaux.append((p, 0.15))
            print(f"Pas 4 phrases nettes : voix posée d'un bloc ({d:.1f} s, ×{tempo:.2f}). Laisser ~1 s de pause entre les phrases pour un calage précis.")
        # assemble la piste voix calée sur 10 s
        entrees, filtres = [], []
        for i, (p, debut) in enumerate(morceaux):
            entrees += ["-i", str(p)]
            ms = int(debut * 1000)
            filtres.append(f"[{i}:a]adelay={ms}|{ms}[d{i}]")
        filtres.append("".join(f"[d{i}]" for i in range(len(morceaux))) +
                       f"amix=inputs={len(morceaux)}:normalize=0,apad=whole_dur=10,atrim=0:10,loudnorm=I=-16:TP=-1.5:LRA=7[v]")
        voix = ICI / "voix_traitee.wav"
        ff(*entrees, "-filter_complex", ";".join(filtres), "-map", "[v]", "-ar", "48000", str(voix))
        # mix voix + musique avec baisse automatique de la musique
        mix = tmp / "mix.wav"
        ff("-i", str(MUSIQUE), "-i", str(voix), "-filter_complex",
           "[1:a]aformat=channel_layouts=stereo,asplit=2[voix][cle];[0:a]volume=-4dB[mus];"
           "[mus][cle]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[musb];"
           "[musb][voix]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9,atrim=0:10[out]",
           "-map", "[out]", "-ar", "48000", str(mix))
        ff("-i", str(VIDEO), "-i", str(mix), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
           "-shortest", "-movflags", "+faststart", str(SORTIE))
    print(f"Vidéo finale : {SORTIE}")


if __name__ == "__main__":
    main()
