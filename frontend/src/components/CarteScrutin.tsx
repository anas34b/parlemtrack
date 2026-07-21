import Link from "next/link";
import type { Scrutin } from "@/types/api";
import RepartitionVotes from "./RepartitionVotes";
import BadgeStatutScrutin from "./BadgeStatutScrutin";

function formaterDate(dateIso: string): string {
  return new Date(dateIso).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

/** Carte d'un scrutin dans le fil d'actualité de l'accueil. */
export default function CarteScrutin({ scrutin }: { scrutin: Scrutin }) {
  return (
    <Link
      href={`/scrutins/${scrutin.uid}`}
      style={{
        display: "block",
        color: "inherit",
        textDecoration: "none",
        background: "var(--couleur-carte)",
        border: "1px solid var(--couleur-bordure)",
        borderRadius: "var(--rayon-carte)",
        padding: "18px 20px",
        boxShadow: "0 1px 2px rgba(0,0,0,0.03)",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 12,
          marginBottom: 10,
        }}
      >
        <span style={{ fontSize: 12.5, fontWeight: 600, color: "var(--couleur-texte-faible)" }}>
          {formaterDate(scrutin.date_scrutin)}
        </span>
        <BadgeStatutScrutin sort={scrutin.sort} />
      </div>
      <h2
        style={{
          fontSize: 17,
          fontWeight: 700,
          margin: "0 0 14px",
          lineHeight: 1.35,
          letterSpacing: "-0.01em",
        }}
      >
        {scrutin.titre}
      </h2>
      <div style={{ marginBottom: 8 }}>
        <RepartitionVotes
          pour={scrutin.nb_pour}
          contre={scrutin.nb_contre}
          abstention={scrutin.nb_abstention}
        />
      </div>
      <div style={{ display: "flex", gap: 16, fontSize: 12.5, color: "var(--couleur-texte-attenue)" }}>
        <span>
          <b style={{ color: "var(--couleur-pour-texte)" }}>{scrutin.nb_pour}</b> pour
        </span>
        <span>
          <b style={{ color: "var(--couleur-contre-texte)" }}>{scrutin.nb_contre}</b> contre
        </span>
        <span>
          <b style={{ color: "var(--couleur-texte-faible)" }}>{scrutin.nb_abstention}</b> abst.
        </span>
      </div>
    </Link>
  );
}
