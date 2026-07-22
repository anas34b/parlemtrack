import type { Metadata } from "next";
import Link from "next/link";
import type { Groupe } from "@/types/api";
import { listerGroupes } from "@/lib/api";

export const metadata: Metadata = {
  title: "Groupes — ParlemTrack",
};

export const dynamic = "force-dynamic";

export default async function GroupesPage() {
  const groupes = await listerGroupes();
  const groupesActifs = groupes.filter((groupe) => groupe.actif);
  const groupesDissous = groupes.filter((groupe) => !groupe.actif);

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em", margin: "4px 0 4px" }}>Groupes</h1>
      <p style={{ fontSize: 14.5, color: "var(--couleur-texte-attenue)", margin: "0 0 20px", lineHeight: 1.5 }}>
        Les groupes politiques de l&rsquo;Assemblée nationale.
      </p>

      <ListeGroupes groupes={groupesActifs} />

      {groupesDissous.length > 0 && (
        <>
          <h2 style={{ fontSize: 13, fontWeight: 700, margin: "24px 0 12px" }}>Groupes dissous</h2>
          <ListeGroupes groupes={groupesDissous} />
        </>
      )}
    </div>
  );
}

function ListeGroupes({ groupes }: { groupes: Groupe[] }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {groupes.map((groupe) => (
        <Link
          key={groupe.id_an}
          href={`/groupes/${groupe.id_an}`}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            background: "var(--couleur-carte)",
            border: "1px solid var(--couleur-bordure)",
            borderRadius: "var(--rayon-carte)",
            padding: "12px 16px",
            color: "inherit",
          }}
        >
          <span
            aria-hidden="true"
            style={{ width: 12, height: 12, borderRadius: 4, background: groupe.couleur ?? "#9ca3af", flexShrink: 0 }}
          />
          <span style={{ flex: 1, fontSize: 13.5, fontWeight: 600 }}>{groupe.nom}</span>
          <span style={{ fontSize: 12, color: "var(--couleur-texte-faible)" }}>{groupe.nom_court}</span>
        </Link>
      ))}
      {groupes.length === 0 && (
        <p style={{ fontSize: 13.5, color: "var(--couleur-texte-faible)" }}>Aucun groupe trouvé.</p>
      )}
    </div>
  );
}
