// Capture d'écran automatique des pages clés de ParlemTrack, desktop + mobile.
//
// Prérequis : docker compose up -d, uvicorn backend.app.main:app (port 8000),
// npm run dev dans frontend/ (port par défaut : 3000, ajustable via BASE_URL).
//
// Usage : node captures.mjs

import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";
const SORTIE = path.join(__dirname, "..", "docs", "captures");

const VIEWPORTS = {
  desktop: { width: 1440, height: 900 },
  mobile: { width: 390, height: 844 },
};

// Identifiants réels (17e législature) utilisés comme exemples de capture.
const PAGES = [
  { nom: "accueil", url: "/" },
  { nom: "scrutin-detail-8427", url: "/scrutins/VTANR5L17V8427" },
  { nom: "scrutin-detail-8418", url: "/scrutins/VTANR5L17V8418" },
  { nom: "depute-fiche", url: "/deputes/PA342415" },
  { nom: "groupe-vue", url: "/groupes/PO845401" },
  { nom: "recherche", url: "/recherche?q=budget" },
  { nom: "comprendre-index", url: "/comprendre" },
  { nom: "comprendre-scrutin", url: "/comprendre/scrutin" },
  { nom: "comprendre-legislature", url: "/comprendre/legislature" },
  { nom: "comprendre-parcours-loi", url: "/comprendre/parcours-loi" },
  { nom: "comprendre-votes-main-levee", url: "/comprendre/votes-main-levee" },
];

async function capturerToutesLesPages() {
  await mkdir(SORTIE, { recursive: true });
  const navigateur = await chromium.launch();

  for (const [formFactor, viewport] of Object.entries(VIEWPORTS)) {
    const contexte = await navigateur.newContext({ viewport });
    const page = await contexte.newPage();

    for (const cible of PAGES) {
      const url = `${BASE_URL}${cible.url}`;
      const fichier = path.join(SORTIE, `${cible.nom}--${formFactor}.png`);
      try {
        await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
        await page.screenshot({ path: fichier, fullPage: true });
        console.log(`OK   ${formFactor.padEnd(7)} ${cible.nom}`);
      } catch (erreur) {
        console.error(`FAIL ${formFactor.padEnd(7)} ${cible.nom} : ${erreur.message}`);
      }
    }

    await contexte.close();
  }

  await navigateur.close();
}

capturerToutesLesPages();
