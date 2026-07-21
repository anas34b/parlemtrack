import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { listerGroupes, obtenirScrutin } from "@/lib/api";
import BadgeStatutScrutin from "@/components/BadgeStatutScrutin";
import BadgeCoherence from "@/components/BadgeCoherence";
import VoteParGroupeBarre from "@/components/VoteParGroupeBarre";
import ArgumentsMiroir from "@/components/ArgumentsMiroir";

function formaterDate(dateIso: string): string {
  return new Date(dateIso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
}

async function chargerScrutin(uid: string) {
  try {
    return await obtenirScrutin(uid);
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ uid: string }>;
}): Promise<Metadata> {
  const { uid } = await params;
  const scrutin = await chargerScrutin(uid);
  return { title: scrutin ? `${scrutin.titre} — ParlemTrack` : "Scrutin introuvable — ParlemTrack" };
}

export default async function DetailScrutinPage({ params }: { params: Promise<{ uid: string }> }) {
  const { uid } = await params;
  const [scrutin, groupes] = await Promise.all([chargerScrutin(uid), listerGroupes()]);
  if (!scrutin) notFound();

  const maxTotal = Math.max(
    1,
    ...scrutin.votes_par_groupe.map((g) => g.pour + g.contre + g.abstention + g.non_votant)
  );
  const couleursParGroupe = new Map(groupes.map((g) => [g.id_an, g.couleur]));

  return (
    <div>
      <Link
        href="/"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          fontSize: 13.5,
          fontWeight: 600,
          color: "var(--couleur-texte-attenue)",
          marginBottom: 18,
        }}
      >
        ← Retour à l&rsquo;accueil
      </Link>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10, marginBottom: 10 }}>
        <span style={{ fontSize: 12.5, fontWeight: 600, color: "var(--couleur-texte-faible)" }}>
          Scrutin n° {scrutin.numero} · {formaterDate(scrutin.date_scrutin)}
        </span>
        <BadgeStatutScrutin sort={scrutin.sort} />
      </div>
      <h1 style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.02em", lineHeight: 1.35, margin: "0 0 6px" }}>
        {scrutin.titre}
      </h1>
      {scrutin.lien_an && (
        <p style={{ fontSize: 13.5, color: "var(--couleur-texte-faible)", lineHeight: 1.5, margin: "0 0 24px" }}>
          <a href={scrutin.lien_an} target="_blank" rel="noopener noreferrer">
            Voir le scrutin sur le site de l&rsquo;Assemblée nationale
          </a>
        </p>
      )}

      <div
        style={{
          background: "var(--couleur-carte)",
          border: "1px solid var(--couleur-bordure)",
          borderRadius: "var(--rayon-carte)",
          padding: 22,
          marginBottom: 20,
        }}
      >
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 20 }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 26, fontWeight: 800, color: "var(--couleur-pour-texte)" }}>
              {scrutin.nb_pour}
            </div>
            <div style={{ fontSize: 12.5, color: "var(--couleur-texte-faible)", fontWeight: 600 }}>pour</div>
          </div>
          <div
            style={{
              textAlign: "center",
              borderLeft: "1px solid var(--couleur-bordure)",
              borderRight: "1px solid var(--couleur-bordure)",
            }}
          >
            <div style={{ fontSize: 26, fontWeight: 800, color: "var(--couleur-contre-texte)" }}>
              {scrutin.nb_contre}
            </div>
            <div style={{ fontSize: 12.5, color: "var(--couleur-texte-faible)", fontWeight: 600 }}>contre</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 26, fontWeight: 800, color: "var(--couleur-texte-faible)" }}>
              {scrutin.nb_abstention}
            </div>
            <div style={{ fontSize: 12.5, color: "var(--couleur-texte-faible)", fontWeight: 600 }}>abstention</div>
          </div>
        </div>

        <h2 style={{ fontSize: 13, fontWeight: 700, margin: "0 0 12px" }}>Vote par groupe</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 11 }}>
          {scrutin.votes_par_groupe.map((vote) => {
            const total = vote.pour + vote.contre + vote.abstention + vote.non_votant;
            return (
              <VoteParGroupeBarre
                key={vote.groupe_id}
                vote={vote}
                couleurGroupe={couleursParGroupe.get(vote.groupe_id) ?? null}
                largeurRelative={(total / maxTotal) * 100}
              />
            );
          })}
        </div>
      </div>

      {scrutin.analyse_ia ? (
        <div
          style={{
            background: "var(--couleur-carte)",
            border: "1px solid var(--couleur-bordure)",
            borderRadius: "var(--rayon-carte)",
            padding: "22px 22px 24px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
            <h2 style={{ fontSize: 13, fontWeight: 700, margin: 0 }}>Analyse</h2>
            <BadgeCoherence coherence={scrutin.analyse_ia.coherence_macro} />
          </div>
          <p style={{ fontSize: 14, lineHeight: 1.6, color: "var(--couleur-texte-secondaire)", margin: "0 0 20px" }}>
            {scrutin.analyse_ia.resume_factuel}
          </p>
          <ArgumentsMiroir
            argumentsPour={scrutin.analyse_ia.arguments_pour}
            argumentsContre={scrutin.analyse_ia.arguments_contre}
          />
          <p style={{ marginTop: 16, fontSize: 12, color: "var(--couleur-texte-tres-faible)" }}>
            Sources : {scrutin.analyse_ia.indicateurs_ref.join(" · ")}
          </p>
        </div>
      ) : (
        <div
          style={{
            background: "var(--couleur-carte)",
            border: "1px solid var(--couleur-bordure)",
            borderRadius: "var(--rayon-carte)",
            padding: 22,
            fontSize: 13.5,
            color: "var(--couleur-texte-faible)",
          }}
        >
          Analyse IA non encore disponible pour ce scrutin.
        </div>
      )}

      <p style={{ fontSize: 12, color: "var(--couleur-texte-tres-faible)", lineHeight: 1.5, margin: "18px 4px 0" }}>
        Note : environ 40 % des votes à l&rsquo;Assemblée nationale ont lieu à main levée et ne sont pas
        comptabilisés nominativement ; ce détail ne couvre que les scrutins publics.
      </p>
    </div>
  );
}
