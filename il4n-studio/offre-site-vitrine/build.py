#!/usr/bin/env python3
"""IL4N STUDIO — génère un site vitrine une page à partir d'un fichier site.json.

Usage : python3 build.py chemin/site.json chemin/sortie/
Produit sortie/index.html (autonome : aucune police, librairie ou image externe) et sortie/mentions-legales.html.
Règles : seules les informations du JSON apparaissent ; aucun avis n'est affiché si la liste "avis" est vide.
"""
import html
import json
import sys
from pathlib import Path

ICONES = {
    "goutte": '<path d="M12 3c3 4.5 6 7.6 6 11a6 6 0 0 1-12 0c0-3.4 3-6.5 6-11z"/>',
    "douche": '<path d="M5 20V8a4 4 0 0 1 8 0"/><path d="M11 8h6"/><path d="M14 12v1M17 12v1M14 16v1M17 16v1M20 12v1"/>',
    "flamme": '<path d="M12 3c1 4 5 5.5 5 10a5 5 0 0 1-10 0c0-2.5 1.5-3.5 2-5 1 1.5 2 2 2 2s-.5-4 1-7z"/>',
    "flocon": '<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9"/><path d="M9.5 4.5 12 6l2.5-1.5M9.5 19.5 12 18l2.5 1.5"/>',
    "outil": '<path d="M14 6a4 4 0 0 0 5 5l-8 8a2 2 0 0 1-3-3z"/>',
    "maison": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    "feuille": '<path d="M5 19c0-9 6-14 15-14 0 9-5 15-14 15"/><path d="M5 19l7-7"/>',
    "tel": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "pinceau": '<path d="M18 3l3 3-9 9-3-3z"/><path d="M9 12c-3 0-5 2-5 5 0 1-1 2-2 2 3 2 8 1 9-4"/>',
}


def e(s):
    return html.escape(str(s), quote=True)


def icone(nom):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONES.get(nom, ICONES["outil"])}</svg>'


def tel_href(t):
    digits = "".join(c for c in t if c.isdigit())
    return "tel:+33" + digits[1:] if digits.startswith("0") else "tel:" + digits


CSS = """
:root{--p:%(principale)s;--a:%(accent)s;--f:%(fond)s;--t:#1d2229;--m:#5a6270;--r:14px}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;color:var(--t);background:var(--f)}
a{color:inherit}
.w{max-width:1080px;margin:0 auto;padding:0 20px}
.fictif{background:#fff3cd;color:#6b4e00;text-align:center;font-size:13px;padding:6px 12px;letter-spacing:.04em}
header{position:sticky;top:0;z-index:10;background:var(--p);color:#fff}
header .w{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:64px}
.logo{font-weight:800;font-size:22px;letter-spacing:.02em;text-decoration:none}
.logo small{display:block;font-weight:500;font-size:12px;opacity:.8;letter-spacing:.06em;text-transform:uppercase}
nav{display:flex;gap:22px;font-size:15px}
nav a{text-decoration:none;opacity:.9}
nav a:hover{opacity:1;text-decoration:underline}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--a);color:#fff;font-weight:700;text-decoration:none;padding:12px 20px;border-radius:999px;border:0;font-size:16px;white-space:nowrap}
.btn:hover{filter:brightness(1.08)}
.btn.ghost{background:transparent;border:2px solid currentColor}
.btn svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2}
.hero{background:var(--p);color:#fff;padding:56px 0 72px;position:relative;overflow:hidden}
.hero .w{position:relative;z-index:1}
.hero:after{content:"";position:absolute;right:-140px;bottom:-200px;width:460px;height:460px;border-radius:50%%;border:70px solid rgba(255,255,255,.06)}
.hero h1{font-size:clamp(30px,5.2vw,52px);line-height:1.1;max-width:15ch;margin:10px 0 16px}
.hero p{font-size:clamp(17px,2.2vw,20px);max-width:52ch;opacity:.92}
.tag{display:inline-block;background:rgba(255,255,255,.14);padding:5px 12px;border-radius:999px;font-size:14px}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px;position:relative;z-index:1}
.atouts{display:flex;flex-wrap:wrap;gap:8px 22px;margin-top:26px;font-size:15px;opacity:.9}
.atouts span:before{content:"✓ ";color:var(--a);font-weight:800}
section{padding:64px 0}
h2{font-size:clamp(26px,3.6vw,36px);line-height:1.2;margin-bottom:8px;color:var(--p)}
.intro{color:var(--m);max-width:60ch;margin-bottom:30px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px}
.card{background:#fff;border-radius:var(--r);padding:24px;box-shadow:0 1px 2px rgba(0,0,0,.06),0 8px 24px rgba(18,59,93,.06)}
.card svg{width:44px;height:44px;padding:9px;border-radius:12px;background:var(--f);fill:none;stroke:var(--a);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;margin-bottom:12px}
.card h3{font-size:19px;margin-bottom:6px}
.card p{color:var(--m);font-size:16px}
.zone{background:#fff}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chips li{list-style:none;background:var(--f);border:1px solid rgba(18,59,93,.12);padding:8px 14px;border-radius:999px;font-size:15px}
.apropos .w{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}
.apropos blockquote{font-size:20px;line-height:1.5;border-left:4px solid var(--a);padding-left:20px}
.avis .card p{color:var(--t);font-style:italic}
.avis .card b{display:block;margin-top:10px;font-style:normal;color:var(--m);font-size:14px}
.contact{background:var(--p);color:#fff}
.contact h2{color:#fff}
.contact .grid{gap:14px}
.contact .card{background:rgba(255,255,255,.08);box-shadow:none;color:#fff}
.contact .card p{color:#fff;opacity:.85}
.contact .card a{font-weight:700;font-size:19px;text-decoration:none;word-break:break-word}
footer{background:#0d2b44;color:#cfd8e3;font-size:14px;padding:22px 0}
footer .w{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px}
.mobile-call{display:none}
header .court{display:none}
@media (max-width:760px){
  nav{display:none}
  header .btn .num{display:none}
  header .court{display:inline}
  header .btn{padding:10px 14px;font-size:15px}
  .hero:after{display:none}
  .apropos .w{grid-template-columns:1fr;gap:20px}
  section{padding:48px 0}
  .mobile-call{display:flex;position:fixed;left:12px;right:12px;bottom:12px;z-index:20;justify-content:center;box-shadow:0 6px 20px rgba(0,0,0,.25)}
  footer{padding-bottom:84px}
}
"""


def page(d, corps, titre, desc):
    css = CSS % d["couleurs"]
    bandeau = '<div class="fictif">CONCEPT FICTIF — IL4N STUDIO · entreprise et coordonnées inventées</div>' if d.get("fictif") else ""
    return f"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(desc)}">
{'<meta name="robots" content="noindex">' if d.get("fictif") else ""}
<meta name="theme-color" content="{e(d["couleurs"]["principale"])}">
<style>{css}</style>
</head><body>
{bandeau}
{corps}
</body></html>
"""


def build(d):
    tel = tel_href(d["telephone"])
    phone_svg = icone("tel")
    services = "".join(f'<article class="card">{icone(s.get("icone"))}<h3>{e(s["titre"])}</h3><p>{e(s["texte"])}</p></article>' for s in d["services"])
    zone = "".join(f"<li>{e(v)}</li>" for v in d["zone"])
    avis = ""
    if d.get("avis"):
        cartes = "".join(f'<figure class="card"><p>« {e(a["texte"])} »</p><b>{e(a["auteur"])}{" · " + e(a["source"]) if a.get("source") else ""}</b></figure>' for a in d["avis"])
        avis = f'<section class="avis"><div class="w"><h2>Ils m’ont fait confiance</h2><p class="intro">Avis publiés par des clients.</p><div class="grid">{cartes}</div></div></section>'
    titre = f'{d["nom"]} — {d["metier"]} à {d["ville"]}'
    corps = f"""
<header><div class="w">
  <a class="logo" href="#">{e(d["nom"])}<small>{e(d["metier"])}</small></a>
  <nav><a href="#services">Services</a><a href="#zone">Secteur</a><a href="#apropos">À propos</a><a href="#contact">Contact</a></nav>
  <a class="btn" href="{tel}" aria-label="Appeler le {e(d["telephone"])}">{phone_svg}<span class="num">{e(d["telephone"])}</span><span class="court">Appeler</span></a>
</div></header>
<main>
<section class="hero"><div class="w">
  <span class="tag">{e(d["metier"])} · {e(d["ville"])}</span>
  <h1>{e(d["accroche"])}</h1>
  <p>{e(d["sous_accroche"])}</p>
  <div class="cta"><a class="btn" href="{tel}">{phone_svg}Appeler</a><a class="btn ghost" href="mailto:{e(d["email"])}?subject={e("Demande de devis")}">Demander un devis</a></div>
  <div class="atouts"><span>Devis gratuit</span><span>Artisan local</span><span>{e(d["horaires"])}</span></div>
</div></section>
<section id="services"><div class="w">
  <h2>Mes services</h2><p class="intro">Ce que je fais pour les particuliers et les professionnels du secteur.</p>
  <div class="grid">{services}</div>
</div></section>
<section id="zone" class="zone"><div class="w">
  <h2>Secteur d’intervention</h2><p class="intro">J’interviens à {e(d["ville"])} et dans les communes voisines :</p>
  <ul class="chips">{zone}</ul>
</div></section>
<section id="apropos" class="apropos"><div class="w">
  <div><h2>À propos</h2><p class="intro">{e(d["nom"])} · {e(d["adresse"])}</p></div>
  <blockquote>{e(d["apropos"])}</blockquote>
</div></section>
{avis}
<section id="contact" class="contact"><div class="w">
  <h2>Contact</h2><p class="intro" style="color:#fff;opacity:.85">Appelez ou écrivez : réponse rapide, devis gratuit.</p>
  <div class="grid">
    <div class="card"><p>Téléphone</p><a href="{tel}">{e(d["telephone"])}</a></div>
    <div class="card"><p>E-mail</p><a href="mailto:{e(d["email"])}">{e(d["email"])}</a></div>
    <div class="card"><p>Horaires</p><b style="font-size:19px">{e(d["horaires"])}</b></div>
  </div>
</div></section>
</main>
<footer><div class="w"><span>© {e(d["nom"])} · {e(d["adresse"])}</span><a href="mentions-legales.html">Mentions légales</a><span>Site réalisé par IL4N STUDIO</span></div></footer>
<a class="btn mobile-call" href="{tel}">{phone_svg}Appeler {e(d["telephone"])}</a>
"""
    index = page(d, corps, titre, f'{d["nom"]}, {d["metier"]} à {d["ville"]} et alentours. {d["sous_accroche"]}')
    m = d["mentions"]
    mentions = page(d, f"""<header><div class="w"><a class="logo" href="index.html">{e(d["nom"])}<small>{e(d["metier"])}</small></a></div></header>
<main><section><div class="w"><h2>Mentions légales</h2>
<p class="intro">Éditeur : {e(m["raison_sociale"])} · SIRET : {e(m["siret"])} · Responsable de la publication : {e(m["responsable"])}<br>
Adresse : {e(d["adresse"])} · Téléphone : {e(d["telephone"])} · E-mail : {e(d["email"])}<br>
Hébergeur : {e(m["hebergeur"])}<br>
Ce site ne dépose aucun cookie et ne collecte aucune donnée personnelle.</p>
<a class="btn" href="index.html">Retour au site</a></div></section></main>""", f'Mentions légales — {d["nom"]}', "Mentions légales")
    return index, mentions


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    d = json.loads(src.read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    index, mentions = build(d)
    (out / "index.html").write_text(index, encoding="utf-8")
    (out / "mentions-legales.html").write_text(mentions, encoding="utf-8")
    print(f"{out/'index.html'} ({len(index)//1024} Ko) + mentions-legales.html")


if __name__ == "__main__":
    main()
