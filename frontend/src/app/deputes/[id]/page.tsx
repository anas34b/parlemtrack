import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { obtenirDepute } from "@/lib/api";
import BadgeMandatTermine from "@/components/BadgeMandatTermine";
import JaugeScore from "@/components/JaugeScore";
import PositionVote from "@/components/PositionVote";

function formaterDate(dateIso: string): string {
  return new Date(dateIso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
}

function initiales(nom: string, prenom: string): string {
  return `${prenom.charAt(0)}${nom.charAt(0)}`.toUpperCase();
}

async function chargerFiche(idAn: string) {
  try {
    return await obtenirDepute(idAn);
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
  const fiche = await chargerFiche(id);
  return {
    title: fiche ? `${fiche.depute.prenom} ${fiche.depute.nom} — ParlemTrack` : "Député introuvable — ParlemTrack",
  };
}

export default async function FicheDeputePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const fiche = await chargerFiche(id);
  if (!fiche) notFound();

  const { depute, historique_votes: historique } = fiche;
  const couleur = depute.groupe?.couleur ?? "#9ca3af";

  return (
    <div>
      <div
        style={{
          background: "var(--couleur-carte)",
          border: "1px solid var(--couleur-bordure)",
          borderRadius: "var(--rayon-carte)",
          padding: 24,
          marginBottom: 18,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18, flexWrap: "wrap" }}>
          <div
            aria-hidden="true"
            style={{
              width: 76,
              height: 76,
              borderRadius: "50%",
              background: "var(--couleur-fond-secondaire)",
              border: `3px solid ${couleur}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 22,
              fontWeight: 800,
              color: "var(--couleur-texte-secondaire)",
              flexShrink: 0,
            }}
          >
            {initiales(depute.nom, depute.prenom)}
          </div>
          <div style={{ flex: 1, minWidth: 180 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 4 }}>
              <h1 style={{ fontSize: 19, fontWeight: 800, margin: 0, letterSpacing: "-0.01em" }}>
                {depute.prenom} {depute.nom}
              </h1>
              {!depute.actif && <BadgeMandatTermine />}
            </div>
            {depute.groupe && (
              <div style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 13.5, color: "var(--couleur-texte-attenue)", marginBottom: 2 }}>
                <span aria-hidden="true" style={{ width: 9, height: 9, borderRadius: 3, background: couleur }} />
                <Link href={`/groupes/${depute.groupe.id_an}`} style={{ fontWeight: 600, color: "inherit" }}>
                  {depute.groupe.nom}
                </Link>
              </div>
            )}
            {depute.circonscription && (
              <div style={{ fontSize: 13, color: "var(--couleur-texte-faible)" }}>{depute.circonscription}</div>
            )}
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 18 }}>
        <JaugeScore label="Participation" valeur={depute.score_participation} couleur="#18181b" />
        <JaugeScore label="Loyauté au groupe" valeur={depute.score_loyaute} couleur={couleur} />
      </div>

      <div
        style={{
          background: "var(--couleur-carte)",
          border: "1px solid var(--couleur-bordure)",
          borderRadius: "var(--rayon-carte)",
          padding: 22,
        }}
      >
        <h2 style={{ fontSize: 13, fontWeight: 700, margin: "0 0 6px" }}>Historique des votes</h2>
        {historique.items.length === 0 ? (
          <p style={{ fontSize: 13.5, color: "var(--couleur-texte-faible)" }}>Aucun vote enregistré.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column" }}>
            {historique.items.map((vote) => (
              <div
                key={vote.scrutin_uid}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "11px 2px",
                  borderBottom: "1px solid #f0f0f1",
                }}
              >
                <div style={{ flex: 1 }}>
                  <Link
                    href={`/scrutins/${vote.scrutin_uid}`}
                    style={{ fontSize: 13.5, fontWeight: 600, color: "var(--couleur-texte)", lineHeight: 1.4 }}
                  >
                    {vote.scrutin_titre}
                  </Link>
                  <div style={{ fontSize: 12, color: "var(--couleur-texte-faible)" }}>
                    {formaterDate(vote.scrutin_date)}
                  </div>
                </div>
                <PositionVote position={vote.position} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
