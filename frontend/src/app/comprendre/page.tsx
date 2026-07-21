import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Comprendre le Parlement — ParlemTrack" };

const ARTICLES = [
  { slug: "scrutin", titre: "Qu'est-ce qu'un scrutin ?" },
  { slug: "legislature", titre: "Qu'est-ce qu'une législature ?" },
  { slug: "parcours-loi", titre: "Le parcours d'une loi" },
  { slug: "votes-main-levee", titre: "Pourquoi ~40 % des votes ne sont pas enregistrés" },
];

export default function ComprendrePage() {
  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em", margin: "4px 0 4px" }}>
        Comprendre le Parlement
      </h1>
      <p style={{ fontSize: 14.5, color: "var(--couleur-texte-attenue)", margin: "0 0 20px", lineHeight: 1.5 }}>
        Des explications simples sur le fonctionnement de l&rsquo;Assemblée nationale.
      </p>
      <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 10 }}>
        {ARTICLES.map((article) => (
          <li key={article.slug}>
            <Link
              href={`/comprendre/${article.slug}`}
              style={{
                display: "block",
                background: "var(--couleur-carte)",
                border: "1px solid var(--couleur-bordure)",
                borderRadius: "var(--rayon-carte)",
                padding: "16px 20px",
                fontSize: 15,
                fontWeight: 600,
                color: "inherit",
              }}
            >
              {article.titre}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
