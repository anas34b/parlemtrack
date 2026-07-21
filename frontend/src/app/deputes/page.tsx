import type { Metadata } from "next";
import Link from "next/link";
import BadgeGroupe from "@/components/BadgeGroupe";
import { listerDeputes } from "@/lib/api";

export const metadata: Metadata = {
  title: "Députés — ParlemTrack",
};

export const revalidate = 60;

const TAILLE_PAGE = 30;

export default async function DeputesPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page } = await searchParams;
  const pageActuelle = Math.max(1, Number(page) || 1);
  // Les députés au mandat terminé sont exclus par défaut de la liste.
  const resultat = await listerDeputes({ page: pageActuelle, tailePage: TAILLE_PAGE, actif: true });

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em", margin: "4px 0 4px" }}>Députés</h1>
      <p style={{ fontSize: 14.5, color: "var(--couleur-texte-attenue)", margin: "0 0 20px", lineHeight: 1.5 }}>
        {resultat.total} député{resultat.total > 1 ? "s" : ""}
        {" "}
        en exercice à l&rsquo;Assemblée nationale.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {resultat.items.map((depute) => (
          <Link
            key={depute.id_an}
            href={`/deputes/${depute.id_an}`}
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
            <span style={{ flex: 1, fontSize: 13.5, fontWeight: 600 }}>
              {depute.prenom} {depute.nom}
            </span>
            {depute.groupe && <BadgeGroupe groupe={depute.groupe} />}
            {depute.circonscription && (
              <span style={{ fontSize: 12, color: "var(--couleur-texte-faible)" }}>{depute.circonscription}</span>
            )}
          </Link>
        ))}
        {resultat.items.length === 0 && (
          <p style={{ fontSize: 13.5, color: "var(--couleur-texte-faible)" }}>Aucun député trouvé.</p>
        )}
      </div>

      <nav aria-label="Pagination" style={{ display: "flex", justifyContent: "space-between", marginTop: 24 }}>
        {pageActuelle > 1 ? <a href={`/deputes?page=${pageActuelle - 1}`}>← Page précédente</a> : <span />}
        {pageActuelle * TAILLE_PAGE < resultat.total && (
          <a href={`/deputes?page=${pageActuelle + 1}`}>Page suivante →</a>
        )}
      </nav>
    </div>
  );
}
