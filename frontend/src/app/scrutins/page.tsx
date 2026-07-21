import type { Metadata } from "next";
import CarteScrutin from "@/components/CarteScrutin";
import { listerScrutins } from "@/lib/api";

export const metadata: Metadata = {
  title: "Scrutins — ParlemTrack",
};

export const revalidate = 60;

const TAILLE_PAGE = 20;

export default async function ScrutinsPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page } = await searchParams;
  const pageActuelle = Math.max(1, Number(page) || 1);
  const resultat = await listerScrutins({ page: pageActuelle, tailePage: TAILLE_PAGE });

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em", margin: "4px 0 4px" }}>Scrutins</h1>
      <p style={{ fontSize: 14.5, color: "var(--couleur-texte-attenue)", margin: "0 0 20px", lineHeight: 1.5 }}>
        {resultat.total} scrutin{resultat.total > 1 ? "s" : ""} enregistré{resultat.total > 1 ? "s" : ""}.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {resultat.items.map((scrutin) => (
          <CarteScrutin key={scrutin.uid} scrutin={scrutin} />
        ))}
      </div>

      <nav aria-label="Pagination" style={{ display: "flex", justifyContent: "space-between", marginTop: 24 }}>
        {pageActuelle > 1 ? <a href={`/scrutins?page=${pageActuelle - 1}`}>← Plus récents</a> : <span />}
        {pageActuelle * TAILLE_PAGE < resultat.total && (
          <a href={`/scrutins?page=${pageActuelle + 1}`}>Scrutins plus anciens →</a>
        )}
      </nav>
    </div>
  );
}
