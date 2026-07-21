import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Qu'est-ce qu'une législature ? — ParlemTrack" };

export default function Page() {
  return (
    <article>
      <Link href="/comprendre" style={{ fontSize: 13.5, fontWeight: 600, color: "var(--couleur-texte-attenue)" }}>
        ← Comprendre le Parlement
      </Link>
      <h1 style={{ fontSize: 22, fontWeight: 800, margin: "14px 0 16px" }}>
        Qu&rsquo;est-ce qu&rsquo;une législature ?
      </h1>
      <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--couleur-texte-secondaire)" }}>
        Une législature désigne la période pendant laquelle une même Assemblée nationale, élue lors d&rsquo;un
        scrutin législatif, exerce son mandat. Sous la Ve République, elle dure en principe cinq ans, sauf
        dissolution anticipée par le président de la République.
      </p>
      <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--couleur-texte-secondaire)" }}>
        Chaque législature est numérotée : ParlemTrack couvre actuellement la 17<sup>e</sup> législature. Les 577
        députés qui la composent sont renouvelés lors des élections législatives suivantes, mais peuvent aussi
        être remplacés en cours de mandat (décès, entrée au gouvernement, invalidation d&rsquo;élection...). Ces
        députés remplacés restent visibles sur ParlemTrack, avec la mention « mandat terminé », car leurs votes
        passés font partie de l&rsquo;historique parlementaire.
      </p>
    </article>
  );
}
