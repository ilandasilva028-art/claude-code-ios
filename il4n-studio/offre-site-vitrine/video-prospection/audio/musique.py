#!/usr/bin/env python3
"""IL4N STUDIO — musique originale de 10 s pour la vidéo de prospection (synthèse locale, aucun droit tiers).

Usage : python3 musique.py sortie.wav
Ré majeur, 120 BPM. Accords : Ré – Si m – Sol – La – Ré.
Accents calés sur la vidéo : entrée du téléphone (2,45 s), prix (5,9 s), logo (7,7 s).
"""
import sys
import wave

import numpy as np

SR = 48000
DUREE = 10.0
N = int(SR * DUREE)
t = np.arange(N) / SR
BEAT = 0.5  # 120 BPM


def note(m):
    """Numéro MIDI → fréquence."""
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a=0.005, d=0.25, s=0.0, r=0.05):
    """Enveloppe ADSR simple sur n échantillons."""
    x = np.zeros(n)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = max(na, 1)
    x[:na] = np.linspace(0, 1, na)
    fin_d = min(n, na + nd)
    x[na:fin_d] = np.linspace(1, s, fin_d - na) if fin_d > na else []
    x[fin_d:] = s
    if nr and n > nr:
        x[-nr:] *= np.linspace(1, 0, nr)
    return x


def passe_bas(x, fc):
    """Filtre passe-bas à un pôle (fc en Hz, peut varier dans le temps)."""
    fc = np.broadcast_to(fc, x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def place(buf, debut, signal, gain=1.0):
    i = int(debut * SR)
    j = min(len(buf), i + len(signal))
    if i < len(buf):
        buf[i:j] += gain * signal[: j - i]


# Accords (MIDI) — 2 s chacun
ACCORDS = [(50, [62, 66, 69]), (47, [62, 66, 71]), (43, [62, 67, 71]), (45, [61, 64, 69]), (50, [62, 66, 69, 74])]

pad = np.zeros(N)
basse = np.zeros(N)
arpege = np.zeros(N)
for k, (b, notes) in enumerate(ACCORDS):
    t0 = k * 2.0
    n = int(2.0 * SR)
    tt = np.arange(n) / SR
    # nappe : 2 dents-de-scie désaccordées par note, attaque douce
    s = np.zeros(n)
    for m in notes:
        f = note(m)
        for det in (-0.12, 0.12):
            ph = (f * 2 ** (det / 12)) * tt
            s += 2 * (ph % 1) - 1
    s *= env(n, a=0.35, d=0.4, s=0.75, r=0.25) / (2 * len(notes))
    place(pad, t0, s)
    # basse : sinus + légère harmonique, une note par temps
    for beat in range(4):
        nb = int(BEAT * SR)
        tb = np.arange(nb) / SR
        fb = note(b - 12)
        sb = (np.sin(2 * np.pi * fb * tb) + 0.25 * np.sin(4 * np.pi * fb * tb)) * env(nb, a=0.004, d=0.4, s=0.3, r=0.05)
        place(basse, t0 + beat * BEAT, sb)
    # arpège en croches (pincé, rond)
    motif = notes + notes[-2:0:-1] if len(notes) > 2 else notes
    for c in range(8):
        m = motif[c % len(motif)] + 12
        nc = int(0.24 * SR)
        tc = np.arange(nc) / SR
        f = note(m)
        sc = (np.sin(2 * np.pi * f * tc) + 0.3 * np.sin(4 * np.pi * f * tc) * np.exp(-tc * 18)) * env(nc, a=0.002, d=0.22, s=0, r=0.01)
        place(arpege, t0 + c * BEAT / 2 + 0.25 * (k == 0 and c == 0), sc)

# le pad s'ouvre progressivement (filtre qui monte) puis se referme sur la fin
fc_pad = np.interp(t, [0, 2.45, 5.9, 7.7, 10], [700, 1400, 2600, 1800, 900])
pad = passe_bas(pad, fc_pad)

# batterie : grosse caisse à partir de l'entrée du téléphone, charleston sur les contretemps
kick = np.zeros(N)
hat = np.zeros(N)
nk = int(0.35 * SR)
tk = np.arange(nk) / SR
k_sig = np.sin(2 * np.pi * (45 * tk + 90 / 30 * (1 - np.exp(-30 * tk)))) * np.exp(-tk * 9)
rng = np.random.default_rng(14)
nh = int(0.06 * SR)
h_sig = passe_bas(rng.standard_normal(nh), 9000) * np.exp(-np.arange(nh) / SR * 70)
h_sig = h_sig - passe_bas(h_sig, 5000)
for i in range(20):
    tb = i * BEAT
    if 2.0 <= tb < 9.5:
        place(kick, tb, k_sig, 0.9)
        place(hat, tb + BEAT / 2, h_sig, 0.5)

# pompage : la nappe respire avec la grosse caisse
pompe = np.ones(N)
for i in range(20):
    tb = i * BEAT
    if 2.0 <= tb < 9.5:
        a = int(tb * SR)
        n = int(0.3 * SR)
        pompe[a:a + n] = np.minimum(pompe[a:a + n], 0.45 + 0.55 * np.linspace(0, 1, n) ** 0.7)

# effets : montée avant le prix, impact au prix, scintillement au logo
fx = np.zeros(N)
nr = int(1.1 * SR)
tr = np.arange(nr) / SR
montee = passe_bas(rng.standard_normal(nr), np.linspace(400, 7000, nr)) * np.linspace(0, 1, nr) ** 2
place(fx, 5.9 - 1.1, montee, 0.35)
ni = int(0.9 * SR)
ti = np.arange(ni) / SR
impact = (np.sin(2 * np.pi * (38 * ti + 60 / 20 * (1 - np.exp(-20 * ti)))) * np.exp(-ti * 5)
          + 0.4 * passe_bas(rng.standard_normal(ni), 3000) * np.exp(-ti * 12))
place(fx, 5.9, impact, 0.8)
ns = int(1.6 * SR)
ts = np.arange(ns) / SR
scint = sum(np.sin(2 * np.pi * note(m) * ts) * np.exp(-ts * 3.2) for m in (86, 90, 93, 98)) / 4
place(fx, 7.7, scint, 0.35)

mix_m = 0.55 * pad * pompe + 0.55 * basse + 0.32 * arpege + 0.7 * kick + 0.18 * hat + fx
# légère stéréo : arpège et scintillement un peu décalés
gauche = mix_m + 0.06 * np.roll(arpege, int(0.012 * SR))
droite = mix_m + 0.06 * np.roll(arpege, int(0.019 * SR))
st = np.stack([gauche, droite], axis=1)
# fondus d'entrée/sortie
st[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
st[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))[:, None] ** 1.5
st /= np.max(np.abs(st)) * 1.12
pcm = (st * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"{sys.argv[1]} : {DUREE:.0f} s, {SR} Hz stéréo")
