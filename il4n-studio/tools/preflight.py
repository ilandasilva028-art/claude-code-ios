#!/usr/bin/env python3
"""IL4N STUDIO — preflight d'un PDF destiné à l'impression.

Usage :
  python3 preflight.py fichier.pdf --trim 148x210 --bleed 3 [--safe 4] [--min-dpi 300] [--min-pt 6]
                       [--cmyk-required] [--pages 1] [--report rapport.md]

Contrôles : nombre de pages, dimensions MediaBox = format fini + fond perdu, TrimBox/BleedBox,
polices incorporées, résolution effective des images, espaces colorimétriques (RGB/CMJN),
texte dans la zone de sécurité, taille minimale des caractères.
Code retour : 0 = OK, 1 = avertissements, 2 = erreurs bloquantes.
"""
import argparse
import re
import sys

import pymupdf

MM = 72 / 25.4
TOL_MM = 0.6


def mm(v):
    return v / MM


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--trim", required=True, help="format fini en mm, ex. 148x210")
    ap.add_argument("--bleed", type=float, default=3)
    ap.add_argument("--safe", type=float, default=4, help="marge de sécurité intérieure en mm")
    ap.add_argument("--min-dpi", type=float, default=300)
    ap.add_argument("--min-pt", type=float, default=6)
    ap.add_argument("--cmyk-required", action="store_true")
    ap.add_argument("--pages", type=int, default=None, help="nombre de pages attendu")
    ap.add_argument("--report", default=None)
    a = ap.parse_args()

    tw, th = (float(x) for x in a.trim.lower().split("x"))
    errors, warns, infos = [], [], []
    doc = pymupdf.open(a.pdf)

    infos.append(f"Fichier : {a.pdf}")
    infos.append(f"Pages : {doc.page_count}")
    if a.pages and doc.page_count != a.pages:
        errors.append(f"{doc.page_count} page(s) au lieu de {a.pages} attendue(s)")

    fonts_seen = {}
    for pno, page in enumerate(doc, start=1):
        mb = page.mediabox
        W, H = mm(mb.width), mm(mb.height)
        eW, eH = tw + 2 * a.bleed, th + 2 * a.bleed
        infos.append(f"p{pno} MediaBox : {W:.1f} × {H:.1f} mm (attendu {eW:.1f} × {eH:.1f})")
        if abs(W - eW) > TOL_MM or abs(H - eH) > TOL_MM:
            errors.append(f"p{pno} dimensions {W:.1f}×{H:.1f} mm ≠ {eW:.1f}×{eH:.1f} mm (format + fond perdu {a.bleed} mm)")

        tb = page.trimbox
        if abs(mm(tb.width) - tw) > TOL_MM or abs(mm(tb.height) - th) > TOL_MM:
            warns.append(f"p{pno} TrimBox {mm(tb.width):.1f}×{mm(tb.height):.1f} mm absente ou ≠ format fini (lancer pdfboxes.py)")

        # Polices
        for f in page.get_fonts(full=True):
            xref, ext, ftype, basefont = f[0], f[1], f[2], f[3]
            fonts_seen[basefont] = ext
            if ext in ("n/a", "") and ftype not in ("Type3",):
                errors.append(f"p{pno} police non incorporée : {basefont} ({ftype})")

        # Images : résolution effective + espace colorimétrique
        for info in page.get_image_info(xrefs=True):
            bbox = pymupdf.Rect(info["bbox"])
            if bbox.width < 2 or bbox.height < 2:
                continue
            ppi_x = info["width"] / (bbox.width / 72)
            ppi_y = info["height"] / (bbox.height / 72)
            ppi = min(ppi_x, ppi_y)
            cs = info.get("cs-name", "?")
            label = f"p{pno} image {info['width']}×{info['height']} px sur {mm(bbox.width):.0f}×{mm(bbox.height):.0f} mm → {ppi:.0f} ppp ({cs})"
            if ppi < a.min_dpi * 0.5:
                errors.append(label + f" — trop faible (< {a.min_dpi*0.5:.0f})")
            elif ppi < a.min_dpi * 0.9:
                warns.append(label + f" — sous {a.min_dpi:.0f} ppp")
            else:
                infos.append(label)
            if a.cmyk_required and "CMYK" not in cs.upper():
                errors.append(label + " — n'est pas en CMJN")

        # Couleurs vectorielles
        try:
            content = page.read_contents()
        except Exception:
            content = b""
        rgb = len(re.findall(rb"\s(?:rg|RG)\b", content))
        cmyk = len(re.findall(rb"\s(?:k|K)\b", content))
        infos.append(f"p{pno} opérateurs couleur : RGB={rgb} CMJN={cmyk}")
        if a.cmyk_required and rgb:
            errors.append(f"p{pno} contient des couleurs RGB alors que l'imprimeur exige du CMJN")

        # Texte : taille mini + zone de sécurité
        trim = pymupdf.Rect(tb) if mm(tb.width) > 1 else pymupdf.Rect(
            a.bleed * MM, a.bleed * MM, (a.bleed + tw) * MM, (a.bleed + th) * MM)
        safe = pymupdf.Rect(trim.x0 + a.safe * MM, trim.y0 + a.safe * MM, trim.x1 - a.safe * MM, trim.y1 - a.safe * MM)
        safe_tol = safe + (-1, -1, 1, 1)  # tolérance d'1 pt pour les jambages
        small, outside = {}, set()
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    txt = span["text"].strip()
                    if not txt:
                        continue
                    if span["size"] < a.min_pt:
                        small[txt[:40]] = min(span["size"], small.get(txt[:40], 99))
                    if not safe_tol.contains(pymupdf.Rect(span["bbox"])):
                        outside.add(f"« {txt[:40]} »")
        for txt, size in sorted(small.items()):
            target = errors if size < a.min_pt - 1 else warns
            target.append(f"p{pno} texte petit : « {txt} » {size:.1f} pt (min {a.min_pt} pt)")
        for s in sorted(outside):
            warns.append(f"p{pno} texte hors zone de sécurité ({a.safe} mm) : {s}")

    infos.append("Polices : " + ", ".join(f"{k} [{v}]" for k, v in fonts_seen.items()) if fonts_seen else "Polices : aucune (texte vectorisé ou absent)")
    if not a.cmyk_required:
        infos.append("Couleur : PDF en RGB/sRGB. Accepté par la plupart des imprimeurs en ligne ; si l'imprimeur exige du CMJN, convertir (tools/cmyk.sh) puis relancer avec --cmyk-required.")

    status = "ÉCHEC" if errors else ("AVERTISSEMENTS" if warns else "CONFORME")
    lines = [f"# Preflight IL4N STUDIO — {status}", "", f"Format fini {tw}×{th} mm · fond perdu {a.bleed} mm · sécurité {a.safe} mm · min {a.min_dpi:.0f} ppp · min {a.min_pt} pt", ""]
    lines += ["## Erreurs bloquantes", *(f"- ❌ {e}" for e in errors or ["aucune"]), ""]
    lines += ["## Avertissements", *(f"- ⚠️ {w}" for w in warns or ["aucun"]), ""]
    lines += ["## Informations", *(f"- {i}" for i in infos)]
    report = "\n".join(lines)
    print(report)
    if a.report:
        with open(a.report, "w", encoding="utf-8") as f:
            f.write(report + "\n")
    sys.exit(2 if errors else (1 if warns else 0))


if __name__ == "__main__":
    main()
