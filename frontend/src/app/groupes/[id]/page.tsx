import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { listerDeputes, obtenirGroupe } from "@/lib/api";

async function chargerGroupe(idAn: string) {
  try {
    return await obtenirGroupe(idAn);
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const groupe = await chargerGroupe(id);
  return { title: groupe ? `${groupe.nom} — ParlemTrack` : "Groupe introuvable — ParlemTrack" };
}

export default async function VueGroupePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const groupe = await chargerGroupe(id);
  if (!groupe) notFound();

  // Les députés au mandat terminé sont exclus par défaut de la composition affichée.
  const composition = await listerDeputes({ groupe: id, actif: true, tailePage: 100 });

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
        <span aria-hidden="true" style={{ width: 14, height: 14, borderRadius: 4, background: groupe.couleur ?? "#9ca3af" }} />
        <h1 style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.02em", margin: 0 }}>{groupe.nom}</h1>
        {!groupe.actif && (
          <span style={{ fontSize: 11, fontWeight: 700, padding: "3px 9px", borderRadius: 999, background: "#f4f4f5", color: "#52525b", border: "1px solid #e4e4e7" }}>
            Groupe dissous
          </span>
        )}
      </div>
      <p style={{ fontSize: 13.5, color: "var(--couleur-texte-faible)", margin: "0 0 24px" }}>
        {groupe.nom_court}
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 24 }}>
        <div style={{ background: "var(--couleur-carte)", border: "1px solid var(--couleur-bordure)", borderRadius: "var(--rayon-carte)", padding: 18, textAlign: "center" }}>
          <div style={{ fontSize: 26, fontWeight: 800 }}>{groupe.effectif}</div>
          <div style={{ fontSize: 12.5, color: "var(--couleur-texte-attenue)", fontWeight: 600 }}>
            député{groupe.effectif > 1 ? "s" : ""} en exercice
          </div>
        </div>
        <div style={{ background: "var(--couleur-carte)", border: "1px solid var(--couleur-bordure)", borderRadius: "var(--rayon-carte)", padding: 18, textAlign: "center" }}>
          <div style={{ fontSize: 26, fontWeight: 800 }}>
            {groupe.cohesion_moyenne !== null ? `${Math.round(groupe.cohesion_moyenne * 100)}%` : "N/A"}
          </div>
          <div style={{ fontSize: 12.5, color: "var(--couleur-texte-attenue)", fontWeight: 600 }}>
            cohésion moyenne des votes
          </div>
        </div>
      </div>

      <h2 style={{ fontSize: 13, fontWeight: 700, margin: "0 0 12px" }}>Composition</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {composition.items.map((depute) => (
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
            {depute.circonscription && (
              <span style={{ fontSize: 12, color: "var(--couleur-texte-faible)" }}>{depute.circonscription}</span>
            )}
          </Link>
        ))}
        {composition.items.length === 0 && (
          <p style={{ fontSize: 13.5, color: "var(--couleur-texte-faible)" }}>Aucun député en exercice.</p>
        )}
      </div>
    </div>
  );
}
