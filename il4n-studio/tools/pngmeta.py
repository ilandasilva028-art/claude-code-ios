#!/usr/bin/env python3
"""Ajuste un PNG à sa taille exacte en pixels et écrit sa résolution (ppp).
Usage : python3 pngmeta.py image.png <largeur_px> <hauteur_px> <dpi>"""
import sys
from PIL import Image

path, w, h, dpi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
im = Image.open(path)
im.load()
if im.size != (w, h):
    if abs(im.width - w) > 4 or abs(im.height - h) > 4:
        print(f"ATTENTION {path} : {im.size} très différent de {w}x{h}, non redimensionné")
    else:
        im = im.resize((w, h), Image.LANCZOS)
im.save(path, dpi=(dpi, dpi), optimize=True)
print(f"{path} : {im.width}x{im.height} px @ {dpi:.0f} ppp")
