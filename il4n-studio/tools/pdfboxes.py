#!/usr/bin/env python3
"""Pose TrimBox / BleedBox sur chaque page d'un PDF (format fini + fond perdu, en mm).
Usage : python3 pdfboxes.py fichier.pdf <largeur_mm> <hauteur_mm> <fond_perdu_mm>
"""
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

MM = 72 / 25.4


def main():
    path, w, h, b = sys.argv[1], *map(float, sys.argv[2:5])
    r = PdfReader(path)
    wr = PdfWriter()
    for p in r.pages:
        mb = p.mediabox
        x0, y0 = float(mb.left), float(mb.bottom)
        full_w, full_h = (w + 2 * b) * MM, (h + 2 * b) * MM
        p.mediabox = RectangleObject([x0, y0, x0 + full_w, y0 + full_h])
        p.cropbox = RectangleObject([x0, y0, x0 + full_w, y0 + full_h])
        p.bleedbox = RectangleObject([x0, y0, x0 + full_w, y0 + full_h])
        p.trimbox = RectangleObject([x0 + b * MM, y0 + b * MM, x0 + (b + w) * MM, y0 + (b + h) * MM])
        p.artbox = p.trimbox
        wr.add_page(p)
    wr.add_metadata({"/Producer": "IL4N STUDIO export", "/Creator": "IL4N STUDIO"})
    with open(path, "wb") as f:
        wr.write(f)
    print(f"TrimBox {w}x{h} mm, BleedBox {w + 2 * b}x{h + 2 * b} mm posées sur {len(r.pages)} page(s)")


if __name__ == "__main__":
    main()
