#!/usr/bin/env python3
"""IL4N STUDIO — rend un PDF en PNG pour le contrôle visuel, avec repères optionnels.

Usage :
  python3 preview.py fichier.pdf --out APERCUS/controle [--dpi 110] [--guides --bleed 3 --safe 4]
Avec --guides : trait rouge = coupe (TrimBox), trait cyan = zone de sécurité, zone grisée = fond perdu.
Produit <out>_p1.png, <out>_p2.png…
"""
import argparse

import pymupdf
from PIL import Image, ImageDraw

MM = 72 / 25.4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--guides", action="store_true")
    ap.add_argument("--bleed", type=float, default=3)
    ap.add_argument("--safe", type=float, default=4)
    a = ap.parse_args()
    doc = pymupdf.open(a.pdf)
    z = a.dpi / 72
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        if a.guides:
            d = ImageDraw.Draw(img, "RGBA")
            b = a.bleed * MM * z
            s = (a.bleed + a.safe) * MM * z
            W, H = img.size
            for rect in [(0, 0, W, b), (0, H - b, W, H), (0, 0, b, H), (W - b, 0, W, H)]:
                d.rectangle(rect, fill=(0, 0, 0, 70))
            d.rectangle((b, b, W - b, H - b), outline=(255, 0, 0, 255), width=2)
            d.rectangle((s, s, W - s, H - s), outline=(0, 200, 255, 255), width=1)
        path = f"{a.out}_p{i}.png"
        img.save(path, optimize=True)
        print(path)


if __name__ == "__main__":
    main()
