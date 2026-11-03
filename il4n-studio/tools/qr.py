#!/usr/bin/env python3
"""IL4N STUDIO — QR codes : génération vectorielle (SVG) et vérification par décodage.

Générer : python3 qr.py make "https://exemple.fr" --out SOURCES/qr.svg [--color "#111111"] [--ec M]
Vérifier : python3 qr.py check EXPORTS/carte_HD.png [--expect "https://exemple.fr"]
Le décodage utilise OpenCV (opencv-python-headless). Code retour 2 si illisible ou contenu différent.
"""
import argparse
import sys


def make(a):
    import qrcode
    import qrcode.image.svg
    ec = {"L": qrcode.constants.ERROR_CORRECT_L, "M": qrcode.constants.ERROR_CORRECT_M,
          "Q": qrcode.constants.ERROR_CORRECT_Q, "H": qrcode.constants.ERROR_CORRECT_H}[a.ec]
    qr = qrcode.QRCode(error_correction=ec, border=4, image_factory=qrcode.image.svg.SvgPathImage)
    qr.add_data(a.data)
    qr.make(fit=True)
    img = qr.make_image()
    svg = img.to_string(encoding="unicode")
    if a.color:
        svg = svg.replace('fill="#000000"', f'fill="{a.color}"')
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"QR SVG : {a.out} (version {qr.version}, correction {a.ec}) → imprimer à 18 mm minimum de côté")


def check(a):
    try:
        import cv2
    except ImportError:
        print("OpenCV absent : pip3 install --user opencv-python-headless")
        sys.exit(3)
    img = cv2.imread(a.image)
    det = cv2.QRCodeDetector()
    ok, decoded, _, _ = det.detectAndDecodeMulti(img)
    found = [d for d in (decoded or []) if d]
    if not found:
        # 2e essai sur image agrandie
        big = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        ok, decoded, _, _ = det.detectAndDecodeMulti(big)
        found = [d for d in (decoded or []) if d]
    if not found:
        print("❌ Aucun QR code lisible")
        sys.exit(2)
    for d in found:
        print(f"QR décodé : {d}")
    if a.expect and a.expect not in found:
        print(f"❌ Contenu attendu « {a.expect} » non trouvé")
        sys.exit(2)
    print("✅ QR code lisible" + (" et conforme" if a.expect else ""))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("data")
    m.add_argument("--out", required=True)
    m.add_argument("--color", default=None)
    m.add_argument("--ec", default="M", choices="LMQH")
    c = sub.add_parser("check")
    c.add_argument("image")
    c.add_argument("--expect", default=None)
    a = ap.parse_args()
    make(a) if a.cmd == "make" else check(a)


if __name__ == "__main__":
    main()
