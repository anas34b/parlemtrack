import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Qu'est-ce qu'un scrutin ? — ParlemTrack" };

export default function Page() {
  return (
    <article>
      <Link href="/comprendre" style={{ fontSize: 13.5, fontWeight: 600, color: "var(--couleur-texte-attenue)" }}>
        ← Comprendre le Parlement
      </Link>
      <h1 style={{ fontSize: 22, fontWeight: 800, margin: "14px 0 16px" }}>Qu&rsquo;est-ce qu&rsquo;un scrutin ?</h1>
      <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--couleur-texte-secondaire)" }}>
        Un scrutin est un vote formel des députés à l&rsquo;Assemblée nationale, sur un article de loi, un
        amendement, une motion, ou l&rsquo;ensemble d&rsquo;un texte. Chaque scrutin donne lieu à un décompte
        officiel des voix : combien de députés ont voté pour, contre, se sont abstenus, ou n&rsquo;ont pas pris
        part au vote.
      </p>
      <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--couleur-texte-secondaire)" }}>
        Il existe plusieurs types de scrutins. Le <strong>scrutin public ordinaire</strong> est le plus courant :
        le vote a lieu par voie électronique et chaque position individuelle est enregistrée nominativement. Le{" "}
        <strong>scrutin public solennel</strong>, plus rare, est utilisé pour les votes les plus importants
        (adoption définitive d&rsquo;un texte majeur, motion de censure...) et se déroule sur plusieurs heures pour
        permettre au plus grand nombre de députés de voter.
      </p>
      <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--couleur-texte-secondaire)" }}>
        ParlemTrack ne recense que les scrutins publics, pour lesquels le nom de chaque votant est connu. Voir
        aussi : <Link href="/comprendre/votes-main-levee">pourquoi une partie des votes n&rsquo;est pas enregistrée</Link>.
      </p>
    </article>
  );
}
