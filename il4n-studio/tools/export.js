#!/usr/bin/env node
// IL4N STUDIO — export d'une page HTML vers PDF (vectoriel) et/ou PNG à la taille exacte.
//
// Impression (le HTML est conçu à la taille FINALE + fond perdu) :
//   node export.js flyer.html --w 148 --h 210 --unit mm --bleed 3 --out EXPORTS/flyer_A5 --pdf --png --dpi 300
// Numérique :
//   node export.js post.html --w 1080 --h 1350 --unit px --out EXPORTS/post_insta --png [--scale 2] [--transparent]
//
// Sorties : <out>_print.pdf (avec fond perdu, TrimBox/BleedBox), <out>_HD.png (format fini, sans fond perdu),
//           <out>_bleed.png (avec fond perdu, si --bleed > 0), ou <out>.png en mode px.
const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');

function loadPlaywright() {
  const tries = [path.join(__dirname, 'node_modules', 'playwright'), 'playwright'];
  for (const t of tries) { try { return require(t); } catch (_) {} }
  console.error('Playwright introuvable. Lancez : cd ~/.claude/il4n-studio/tools && npm install playwright && npx playwright install chromium');
  process.exit(2);
}

function parseArgs(argv) {
  const a = { unit: 'mm', bleed: 0, dpi: 300, pdf: false, png: false, scale: 1, transparent: false };
  a.input = argv[0];
  for (let i = 1; i < argv.length; i++) {
    const k = argv[i];
    const v = argv[i + 1];
    if (k === '--w') { a.w = parseFloat(v); i++; }
    else if (k === '--h') { a.h = parseFloat(v); i++; }
    else if (k === '--unit') { a.unit = v; i++; }
    else if (k === '--bleed') { a.bleed = parseFloat(v); i++; }
    else if (k === '--dpi') { a.dpi = parseFloat(v); i++; }
    else if (k === '--scale') { a.scale = parseFloat(v); i++; }
    else if (k === '--out') { a.out = v; i++; }
    else if (k === '--pdf') a.pdf = true;
    else if (k === '--png') a.png = true;
    else if (k === '--transparent') a.transparent = true;
  }
  if (!a.input || !a.w || !a.h || !a.out) {
    console.error('Usage: node export.js page.html --w <largeur> --h <hauteur> [--unit mm|px] [--bleed mm] [--dpi 300] --out <chemin_sans_ext> [--pdf] [--png]');
    process.exit(1);
  }
  if (!a.pdf && !a.png) { a.png = true; if (a.unit === 'mm') a.pdf = true; }
  return a;
}

(async () => {
  const a = parseArgs(process.argv.slice(2));
  const { chromium } = loadPlaywright();
  const MM = 96 / 25.4; // px CSS par mm
  const isPrint = a.unit === 'mm';
  const fullW = isPrint ? a.w + 2 * a.bleed : a.w;
  const fullH = isPrint ? a.h + 2 * a.bleed : a.h;
  const vpW = Math.round(isPrint ? fullW * MM : fullW);
  const vpH = Math.round(isPrint ? fullH * MM : fullH);
  const dsf = isPrint ? a.dpi / 96 : a.scale;

  fs.mkdirSync(path.dirname(path.resolve(a.out)), { recursive: true });
  const launchOpts = process.env.IL4N_CHROMIUM ? { executablePath: process.env.IL4N_CHROMIUM } : {};
  const browser = await chromium.launch(launchOpts);
  const page = await browser.newPage({ viewport: { width: vpW, height: vpH }, deviceScaleFactor: dsf });
  await page.goto('file://' + path.resolve(a.input), { waitUntil: 'networkidle' });
  await page.evaluate(async () => { await document.fonts.ready; });
  // Avertit si des images ne sont pas chargées
  const broken = await page.evaluate(() => [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src));
  if (broken.length) console.warn('ATTENTION images non chargées :', broken.join(', '));
  // Avertit si le contenu déborde la page
  const overflow = await page.evaluate(() => ({ w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight }));
  if (overflow.w > vpW + 1 || overflow.h > vpH + 1) console.warn(`ATTENTION contenu plus grand que la page : ${overflow.w}x${overflow.h}px pour ${vpW}x${vpH}px`);

  const outputs = [];
  if (a.png) {
    if (isPrint) {
      const hd = `${a.out}_HD.png`;
      const b = a.bleed * MM;
      await page.screenshot({ path: hd, clip: { x: b, y: b, width: a.w * MM, height: a.h * MM } });
      outputs.push(hd);
      if (a.bleed > 0) {
        const bl = `${a.out}_bleed.png`;
        await page.screenshot({ path: bl, clip: { x: 0, y: 0, width: vpW, height: vpH } });
        outputs.push(bl);
      }
    } else {
      const p = `${a.out}.png`;
      await page.screenshot({ path: p, clip: { x: 0, y: 0, width: vpW, height: vpH }, omitBackground: a.transparent });
      outputs.push(p);
    }
  }
  if (a.pdf) {
    const pdfPath = isPrint ? `${a.out}_print.pdf` : `${a.out}.pdf`;
    await page.emulateMedia({ media: 'print' });
    await page.pdf({
      path: pdfPath,
      width: isPrint ? `${fullW}mm` : `${fullW}px`,
      height: isPrint ? `${fullH}mm` : `${fullH}px`,
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
      pageRanges: '',
    });
    if (isPrint) {
      try {
        execFileSync('python3', [path.join(__dirname, 'pdfboxes.py'), pdfPath, String(a.w), String(a.h), String(a.bleed)], { stdio: 'inherit' });
      } catch (e) { console.warn('ATTENTION TrimBox/BleedBox non posées :', e.message); }
    }
    outputs.push(pdfPath);
  }
  await browser.close();
  console.log('Exports :\n' + outputs.map(o => '  ' + o).join('\n'));
})().catch(e => { console.error(e); process.exit(1); });
