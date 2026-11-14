#!/usr/bin/env python3
"""IL4N STUDIO — génère un site vitrine une page à partir d'un fichier site.json.

Usage : python3 build.py chemin/site.json chemin/sortie/
Produit sortie/index.html, sortie/mentions-legales.html et sortie/assets/ (logo, police, film).
Aucune librairie, police ou image externe ; aucun cookie.
Règle IL4N : seules les informations du JSON apparaissent. Promesses (atouts), avis et horaires
ne s'affichent que s'ils sont fournis par le client.
"""
import base64
import html
import json
import shutil
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
    "pinceau": '<path d="M18 3l3 3-9 9-3-3z"/><path d="M9 12c-3 0-5 2-5 5 0 1-1 2-2 2 3 2 8 1 9-4"/>',
    "tel": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
}
# Motif de marque : trois rafales (reprend le symbole)
MOTIF = '<svg class="motif" viewBox="0 0 40 16" aria-hidden="true"><path d="M2 3h18M2 8h28M2 13h12"/></svg>'


def e(s):
    return html.escape(str(s), quote=True)


def icone(nom):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONES.get(nom, ICONES["outil"])}</svg>'


def tel_href(t):
    digits = "".join(c for c in t if c.isdigit())
    return "tel:+33" + digits[1:] if digits.startswith("0") else "tel:" + digits


CSS = """
%(fontface)s
:root{--p:%(principale)s;--a:%(accent)s;--f:%(fond)s;--eau:%(eau)s;--t:#17202b;--m:#566170;--r:18px;
--titre:%(titre)s;--texte:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font:17px/1.65 var(--texte);color:var(--t);background:var(--f)}
a{color:inherit}
h1,h2,h3,.logo b{font-family:var(--titre);font-weight:750;letter-spacing:-.02em}
.w{max-width:1120px;margin:0 auto;padding:0 20px}
.fictif{background:#fff3cd;color:#6b4e00;text-align:center;font-size:13px;padding:6px 12px;letter-spacing:.04em}
header{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--p) 94%%,transparent);backdrop-filter:blur(8px);color:#fff}
header .w{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:70px}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none}
.logo svg{width:40px;height:40px;flex:none}
.logo b{display:block;font-size:24px;line-height:1}
.logo small{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;opacity:.75;margin-top:3px}
nav{display:flex;gap:24px;font-size:15px}
nav a{text-decoration:none;opacity:.88}
nav a:hover{opacity:1;color:var(--a)}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--a);color:#fff;font-weight:700;text-decoration:none;padding:13px 22px;border-radius:999px;border:0;font-size:16px;white-space:nowrap;transition:transform .15s,filter .15s}
.btn:hover{filter:brightness(1.08);transform:translateY(-1px)}
.btn.ghost{background:transparent;border:2px solid rgba(255,255,255,.55)}
.btn svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2}
header .court{display:none}
.hero{background:var(--p);color:#fff;padding:56px 0 80px;overflow:hidden}
.hero .w{display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:center}
.hero h1{font-size:clamp(34px,5.4vw,60px);line-height:1.04;margin:16px 0 18px}
.hero h1 em{font-style:normal;color:var(--a)}
.hero p{font-size:clamp(17px,2vw,20px);max-width:48ch;opacity:.9}
.tag{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.1);padding:6px 14px;border-radius:999px;font-size:14px}
.tag:before{content:"";width:8px;height:8px;border-radius:50%%;background:var(--eau)}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:30px}
.atouts{display:flex;flex-wrap:wrap;gap:8px 22px;margin-top:28px;font-size:15px;opacity:.9;list-style:none}
.atouts li:before{content:"✓ ";color:var(--a);font-weight:800}
.film{position:relative;aspect-ratio:1;border-radius:28px;overflow:hidden;background:var(--p);box-shadow:0 30px 60px rgba(0,0,0,.35),0 0 0 1px rgba(255,255,255,.08)}
.film video,.film img{width:100%%;height:100%%;object-fit:cover;display:block}
.film img{position:absolute;inset:0}
.film video{position:relative;z-index:1}
section{padding:80px 0}
.titre{display:flex;align-items:center;gap:12px;margin-bottom:10px}
.motif{width:40px;height:16px;flex:none;fill:none;stroke:var(--a);stroke-width:3;stroke-linecap:round}
h2{font-size:clamp(28px,3.8vw,42px);line-height:1.1;color:var(--p)}
.intro{color:var(--m);max-width:60ch;margin-bottom:34px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}
.card{position:relative;background:#fff;border-radius:var(--r);padding:28px 24px 24px;box-shadow:0 1px 2px rgba(0,0,0,.05),0 12px 30px rgba(14,42,71,.07);transition:transform .2s}
.card:hover{transform:translateY(-3px)}
.card .num{position:absolute;top:22px;right:24px;font-family:var(--titre);font-weight:700;color:var(--a);opacity:.5;font-size:15px}
.card svg{width:48px;height:48px;padding:10px;border-radius:14px;background:var(--f);fill:none;stroke:var(--a);stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;margin-bottom:14px}
.card h3{font-size:21px;line-height:1.25;margin-bottom:8px;color:var(--p)}
.card p{color:var(--m);font-size:16px}
.zone{background:#fff}
.chips{display:flex;flex-wrap:wrap;gap:10px;list-style:none}
.chips li{background:var(--f);border:1px solid rgba(14,42,71,.12);padding:9px 16px;border-radius:999px;font-size:15px}
.chips li:first-child{background:var(--p);color:#fff;border-color:var(--p)}
.apropos .w{display:grid;grid-template-columns:.8fr 1.2fr;gap:48px;align-items:center}
.apropos blockquote{font-family:var(--titre);font-size:clamp(22px,2.6vw,30px);line-height:1.3;color:var(--p);font-weight:600;letter-spacing:-.01em}
.apropos blockquote:before{content:"“";display:block;font-size:80px;line-height:.6;color:var(--a);margin-bottom:12px}
.avis .card p{color:var(--t);font-style:italic}
.avis .card b{display:block;margin-top:10px;font-style:normal;color:var(--m);font-size:14px}
.contact{background:var(--p);color:#fff;position:relative;overflow:hidden}
.contact h2{color:#fff}
.contact .intro{color:#fff;opacity:.85}
.contact .grid{gap:14px}
.contact .card{background:rgba(255,255,255,.07);box-shadow:none;color:#fff;border:1px solid rgba(255,255,255,.1)}
.contact .card p{color:#fff;opacity:.75;font-size:14px;text-transform:uppercase;letter-spacing:.1em}
.contact .card a,.contact .card b{font-family:var(--titre);font-weight:700;font-size:21px;text-decoration:none;word-break:break-word}
footer{background:color-mix(in srgb,var(--p) 80%%,#000);color:#cfd8e3;font-size:14px;padding:26px 0}
footer .w{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px}
footer .logo svg{width:28px;height:28px}
footer .logo b{font-size:18px}
.mobile-call{display:none}
.reveal{opacity:0;transform:translateY(18px);transition:opacity .6s ease,transform .6s ease}
.reveal.vu{opacity:1;transform:none}
@media (prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none}.film video{display:none}.btn,.card{transition:none}}
@media (max-width:860px){
  nav{display:none}
  header .btn .num{display:none}
  header .court{display:inline}
  header .logo small{display:none}
  header .btn{padding:10px 16px;font-size:15px}
  .hero{padding:36px 0 56px}
  .hero .w{grid-template-columns:1fr;gap:32px}
  .film{max-width:420px;width:100%%;justify-self:center}
  .apropos .w{grid-template-columns:1fr;gap:16px}
  section{padding:56px 0}
  .mobile-call{display:flex;position:fixed;left:12px;right:12px;bottom:12px;z-index:20;justify-content:center;box-shadow:0 8px 24px rgba(0,0,0,.3)}
  footer{padding-bottom:90px}
}
"""

REVEAL_JS = """<script>
(function(){var els=document.querySelectorAll('.reveal');if(!('IntersectionObserver' in window)){els.forEach(function(x){x.classList.add('vu')});return}
var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('vu');io.unobserve(x.target)}})},{threshold:.12});
els.forEach(function(x){io.observe(x)})})();
</script>"""


def page(d, corps, titre, desc, ctx, script=""):
    c = dict(d["couleurs"])
    c.setdefault("eau", c["accent"])
    c["fontface"] = ctx["fontface"]
    c["titre"] = ctx["police"]
    css = CSS % c
    bandeau = '<div class="fictif">CONCEPT FICTIF — IL4N STUDIO · entreprise et coordonnées inventées</div>' if d.get("fictif") else ""
    favicon = f'<link rel="icon" href="{ctx["favicon"]}">' if ctx["favicon"] else ""
    return f"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(desc)}">
{'<meta name="robots" content="noindex">' if d.get("fictif") else ""}
<meta name="theme-color" content="{e(c["principale"])}">
{favicon}
{ctx["preload"]}
<style>{css}</style>
</head><body>
{bandeau}
{corps}
{script}
</body></html>
"""


def preparer_marque(d, src_dir, out):
    """Copie les fichiers de marque dans out/assets et prépare logo, police, favicon, film."""
    m = d.get("marque", {})
    assets = out / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    ctx = {"logo": "", "fontface": "", "police": "var(--texte)", "preload": "", "favicon": "", "film": ""}
    if m.get("logo"):
        svg = (src_dir / m["logo"]).read_text(encoding="utf-8")
        svg = svg.split("?>")[-1].strip()
        ctx["logo"] = svg.replace("<svg ", '<svg aria-hidden="true" ', 1)
        ctx["favicon"] = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
    if m.get("police_titre"):
        f = src_dir / m["police_titre"]
        shutil.copy(f, assets / f.name)
        ctx["fontface"] = f'@font-face{{font-family:"Titre";src:url(assets/{f.name}) format("woff2");font-weight:200 800;font-display:swap}}'
        ctx["police"] = '"Titre",var(--texte)'
        ctx["preload"] = f'<link rel="preload" href="assets/{f.name}" as="font" type="font/woff2" crossorigin>'
    if m.get("film_mp4"):
        v = src_dir / m["film_mp4"]
        shutil.copy(v, assets / v.name)
        poster = ""
        if m.get("film_poster"):
            p = src_dir / m["film_poster"]
            shutil.copy(p, assets / p.name)
            poster = f"assets/{p.name}"
        img = f'<img src="{poster}" alt="" aria-hidden="true">' if poster else ""
        ctx["film"] = (f'<div class="film">{img}<video autoplay muted loop playsinline preload="metadata"'
                       f'{" poster=" + chr(34) + poster + chr(34) if poster else ""} aria-hidden="true">'
                       f'<source src="assets/{v.name}" type="video/mp4"></video></div>')
    return ctx


def build(d, ctx):
    tel = tel_href(d["telephone"])
    tsvg = icone("tel")
    logo = f'<a class="logo" href="#">{ctx["logo"]}<span><b>{e(d["nom"])}</b><small>{e(d["metier"])}</small></span></a>'
    services = "".join(
        f'<article class="card reveal"><span class="num">{i:02d}</span>{icone(s.get("icone"))}<h3>{e(s["titre"])}</h3><p>{e(s["texte"])}</p></article>'
        for i, s in enumerate(d["services"], 1))
    zone = "".join(f"<li>{e(v)}</li>" for v in d["zone"])
    atouts = "".join(f"<li>{e(a)}</li>" for a in d.get("atouts", []))
    atouts = f'<ul class="atouts">{atouts}</ul>' if atouts else ""
    accroche = e(d["accroche"])
    if d.get("accroche_accent") and d["accroche_accent"] in d["accroche"]:
        accroche = accroche.replace(e(d["accroche_accent"]), f'<em>{e(d["accroche_accent"])}</em>', 1)
    avis = ""
    if d.get("avis"):
        cartes = "".join(f'<figure class="card reveal"><p>« {e(a["texte"])} »</p><b>{e(a["auteur"])}{" · " + e(a["source"]) if a.get("source") else ""}</b></figure>' for a in d["avis"])
        avis = f'<section class="avis"><div class="w"><div class="titre">{MOTIF}<h2>Ils m’ont fait confiance</h2></div><p class="intro">Avis publiés par des clients.</p><div class="grid">{cartes}</div></div></section>'
    horaires = f'<div class="card"><p>Horaires</p><b>{e(d["horaires"])}</b></div>' if d.get("horaires") else ""
    contact_intro = e(d.get("contact_intro", "Appelez ou écrivez-moi."))
    corps = f"""
<header><div class="w">
  {logo}
  <nav><a href="#services">Services</a><a href="#zone">Secteur</a><a href="#apropos">À propos</a><a href="#contact">Contact</a></nav>
  <a class="btn" href="{tel}" aria-label="Appeler le {e(d["telephone"])}">{tsvg}<span class="num">{e(d["telephone"])}</span><span class="court">Appeler</span></a>
</div></header>
<main>
<section class="hero"><div class="w">
  <div>
    <span class="tag">{e(d.get("tag", d["ville"]))}</span>
    <h1>{accroche}</h1>
    <p>{e(d["sous_accroche"])}</p>
    <div class="cta"><a class="btn" href="{tel}">{tsvg}Appeler</a><a class="btn ghost" href="mailto:{e(d["email"])}?subject={e("Demande de devis")}">Écrire un e-mail</a></div>
    {atouts}
  </div>
  {ctx["film"]}
</div></section>
<section id="services"><div class="w">
  <div class="titre">{MOTIF}<h2>Mes services</h2></div>
  <p class="intro">{e(d.get("services_intro", "Ce que je fais pour vous."))}</p>
  <div class="grid">{services}</div>
</div></section>
<section id="zone" class="zone"><div class="w">
  <div class="titre">{MOTIF}<h2>Secteur d’intervention</h2></div>
  <p class="intro">J’interviens à {e(d["ville"])} et dans les communes voisines :</p>
  <ul class="chips reveal">{zone}</ul>
</div></section>
<section id="apropos" class="apropos"><div class="w">
  <div><div class="titre">{MOTIF}<h2>À propos</h2></div><p class="intro">{e(d["nom"])} · {e(d["adresse"])}</p></div>
  <blockquote class="reveal">{e(d["apropos"])}</blockquote>
</div></section>
{avis}
<section id="contact" class="contact"><div class="w">
  <div class="titre">{MOTIF}<h2>Contact</h2></div>
  <p class="intro">{contact_intro}</p>
  <div class="grid">
    <div class="card"><p>Téléphone</p><a href="{tel}">{e(d["telephone"])}</a></div>
    <div class="card"><p>E-mail</p><a href="mailto:{e(d["email"])}">{e(d["email"])}</a></div>
    {horaires}
  </div>
</div></section>
</main>
<footer><div class="w">{logo.replace('href="#"', 'href="#" aria-label="Haut de page"')}<a href="mentions-legales.html">Mentions légales</a><span>Site réalisé par IL4N STUDIO</span></div></footer>
<a class="btn mobile-call" href="{tel}">{tsvg}Appeler {e(d["telephone"])}</a>
"""
    index = page(d, corps, f'{d["nom"]} — {d["metier"]} à {d["ville"]}',
                 f'{d["nom"]}, {d["metier"]} à {d["ville"]} et alentours. {d["sous_accroche"]}', ctx, REVEAL_JS)
    m = d["mentions"]
    mentions = page(d, f"""<header><div class="w">{logo.replace('href="#"', 'href="index.html"')}</div></header>
<main><section><div class="w"><div class="titre">{MOTIF}<h2>Mentions légales</h2></div>
<p class="intro">Éditeur : {e(m["raison_sociale"])} · SIRET : {e(m["siret"])} · Responsable de la publication : {e(m["responsable"])}<br>
Adresse : {e(d["adresse"])} · Téléphone : {e(d["telephone"])} · E-mail : {e(d["email"])}<br>
Hébergeur : {e(m["hebergeur"])}<br>
Ce site ne dépose aucun cookie et ne collecte aucune donnée personnelle.</p>
<a class="btn" href="index.html">Retour au site</a></div></section></main>""", f'Mentions légales — {d["nom"]}', "Mentions légales", ctx)
    return index, mentions


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    d = json.loads(src.read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    ctx = preparer_marque(d, src.parent, out)
    index, mentions = build(d, ctx)
    (out / "index.html").write_text(index, encoding="utf-8")
    (out / "mentions-legales.html").write_text(mentions, encoding="utf-8")
    poids = sum(f.stat().st_size for f in out.rglob("*") if f.is_file()) // 1024
    print(f"{out/'index.html'} — site complet : {poids} Ko")


if __name__ == "__main__":
    main()
