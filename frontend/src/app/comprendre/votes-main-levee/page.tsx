import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Pourquoi ~40 % des votes ne sont pas enregistrés — ParlemTrack",
};

export default function Page() {
  return (
    <article>
      <Link href="/comprendre" style={{ fontSize: 13.5, fontWeight: 600, color: "var(--couleur-texte-attenue)" }}>
        ← Comprendre le Parlement
      </Link>
      <h1 style={{ fontSize: 22, fontWeight: 800, margin: "14px 0 16px" }}>
        Pourquoi environ 40 % des votes ne sont pas enregistrés
      </h1>
      <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--couleur-texte-secondaire)" }}>
        À l&rsquo;Assemblée nationale, tous les votes ne donnent pas lieu à un scrutin public. Une grande partie
        des votes se déroule <strong>à main levée</strong> : le président de séance évalue à l&rsquo;œil le
        résultat (« adopté » ou « rejeté ») sans décompte individuel des voix. Ce mode de vote, plus rapide, est
        utilisé par défaut pour la majorité des textes, notamment lorsque le résultat ne fait pas débat.
      </p>
      <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--couleur-texte-secondaire)" }}>
        Un scrutin public — avec décompte nominatif de chaque député — n&rsquo;a lieu que sur demande explicite
        (d&rsquo;un président de groupe, du gouvernement, ou dans les cas prévus par le règlement de
        l&rsquo;Assemblée, comme les motions de censure ou certains votes solennels).
      </p>
      <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--couleur-texte-secondaire)" }}>
        <strong>ParlemTrack ne peut donc recenser que les scrutins publics : les votes à main levée ne sont, par
        nature, pas traçables individuellement.</strong> Les scrutins publics présentés sur ce site représentent
        une part significative mais partielle de l&rsquo;activité législative de l&rsquo;Assemblée.
      </p>
    </article>
  );
}
