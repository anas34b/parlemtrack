import type { Metadata } from "next";
import CarteScrutin from "@/components/CarteScrutin";
import BandeauActualites from "@/components/BandeauActualites";
import { listerScrutins } from "@/lib/api";

export const metadata: Metadata = {
  title: "ParlemTrack — Derniers scrutins de l'Assemblée nationale",
};

export const revalidate = 60;

export default async function AccueilPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page } = await searchParams;
  const pageActuelle = Math.max(1, Number(page) || 1);
  const resultat = await listerScrutins({ page: pageActuelle, tailePage: 20 });

  return (
    <div>
      <div style={{ marginTop: -24, marginInline: -20, marginBottom: 20 }}>
        <BandeauActualites />
      </div>
      <h1 style={{ fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em", margin: "4px 0 4px" }}>
        Derniers scrutins
      </h1>
      <p style={{ fontSize: 14.5, color: "var(--couleur-texte-attenue)", margin: "0 0 20px", lineHeight: 1.5 }}>
        Les votes de l&rsquo;Assemblée nationale, expliqués simplement.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {resultat.items.map((scrutin) => (
          <CarteScrutin key={scrutin.uid} scrutin={scrutin} />
        ))}
      </div>

      <nav aria-label="Pagination" style={{ display: "flex", justifyContent: "space-between", marginTop: 24 }}>
        {pageActuelle > 1 ? <a href={`/?page=${pageActuelle - 1}`}>← Plus récents</a> : <span />}
        {pageActuelle * 20 < resultat.total && <a href={`/?page=${pageActuelle + 1}`}>Scrutins plus anciens →</a>}
      </nav>
    </div>
  );
}
