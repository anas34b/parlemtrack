import type { Metadata } from "next";
import Link from "next/link";
import { rechercher } from "@/lib/api";
import BadgeMandatTermine from "@/components/BadgeMandatTermine";

export const metadata: Metadata = { title: "Recherche — ParlemTrack" };

export default async function RecherchePage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const requete = (q ?? "").trim();
  const resultat = requete ? await rechercher(requete) : null;
  const total = resultat ? resultat.deputes.length + resultat.groupes.length + resultat.scrutins.length : 0;

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.02em", margin: "0 0 20px" }}>
        {requete ? (
          <>
            Résultats pour « {requete} »
          </>
        ) : (
          "Recherche"
        )}
      </h1>

      {!requete && (
        <p style={{ fontSize: 14, color: "var(--couleur-texte-faible)" }}>
          Utilisez la barre de recherche en haut de page pour trouver un scrutin, un député ou un groupe.
        </p>
      )}

      {requete && total === 0 && (
        <p style={{ fontSize: 14, color: "var(--couleur-texte-faible)" }}>Aucun résultat pour « {requete} ».</p>
      )}

      {resultat && resultat.deputes.length > 0 && (
        <section style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.03em", color: "var(--couleur-texte-faible)", marginBottom: 10 }}>
            Députés
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {resultat.deputes.map((depute) => (
              <Link
                key={depute.id_an}
                href={`/deputes/${depute.id_an}`}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
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
                {!depute.actif && <BadgeMandatTermine />}
                {depute.groupe && (
                  <span style={{ fontSize: 12, color: "var(--couleur-texte-faible)" }}>{depute.groupe.nom_court}</span>
                )}
              </Link>
            ))}
          </div>
        </section>
      )}

      {resultat && resultat.groupes.length > 0 && (
        <section style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.03em", color: "var(--couleur-texte-faible)", marginBottom: 10 }}>
            Groupes
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {resultat.groupes.map((groupe) => (
              <Link
                key={groupe.id_an}
                href={`/groupes/${groupe.id_an}`}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  background: "var(--couleur-carte)",
                  border: "1px solid var(--couleur-bordure)",
                  borderRadius: "var(--rayon-carte)",
                  padding: "12px 16px",
                  color: "inherit",
                }}
              >
                <span aria-hidden="true" style={{ width: 9, height: 9, borderRadius: 3, background: groupe.couleur ?? "#9ca3af" }} />
                <span style={{ fontSize: 13.5, fontWeight: 600 }}>{groupe.nom}</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {resultat && resultat.scrutins.length > 0 && (
        <section>
          <h2 style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.03em", color: "var(--couleur-texte-faible)", marginBottom: 10 }}>
            Scrutins
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {resultat.scrutins.map((scrutin) => (
              <Link
                key={scrutin.uid}
                href={`/scrutins/${scrutin.uid}`}
                style={{
                  display: "block",
                  background: "var(--couleur-carte)",
                  border: "1px solid var(--couleur-bordure)",
                  borderRadius: "var(--rayon-carte)",
                  padding: "12px 16px",
                  color: "inherit",
                  fontSize: 13.5,
                  fontWeight: 600,
                }}
              >
                {scrutin.titre}
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
