import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Le parcours d'une loi — ParlemTrack" };

const ETAPES = [
  {
    titre: "Dépôt du texte",
    texte:
      "Un projet de loi (déposé par le gouvernement) ou une proposition de loi (déposée par un parlementaire) est enregistré à l'Assemblée nationale ou au Sénat.",
  },
  {
    titre: "Examen en commission",
    texte:
      "Une commission parlementaire examine le texte, l'amende et rédige un rapport avant son passage en séance publique.",
  },
  {
    titre: "Discussion en séance publique",
    texte:
      "Les députés débattent du texte article par article, déposent et votent des amendements, puis votent l'ensemble du texte.",
  },
  {
    titre: "Navette entre les deux chambres",
    texte:
      "Le texte adopté est transmis à l'autre chambre (Sénat ou Assemblée). Chaque chambre doit l'adopter dans les mêmes termes ; sinon, la navette se poursuit.",
  },
  {
    titre: "Commission mixte paritaire (si désaccord persistant)",
    texte:
      "En cas de désaccord après plusieurs lectures, une commission mixte paritaire réunissant députés et sénateurs tente d'élaborer un texte de compromis.",
  },
  {
    titre: "Dernier mot à l'Assemblée nationale",
    texte:
      "Si le désaccord persiste, le gouvernement peut donner le dernier mot à l'Assemblée nationale, qui adopte alors le texte définitif.",
  },
  {
    titre: "Promulgation",
    texte:
      "Une fois définitivement adopté, le texte est promulgué par le président de la République et publié au Journal officiel : il devient loi.",
  },
];

export default function Page() {
  return (
    <article>
      <Link href="/comprendre" style={{ fontSize: 13.5, fontWeight: 600, color: "var(--couleur-texte-attenue)" }}>
        ← Comprendre le Parlement
      </Link>
      <h1 style={{ fontSize: 22, fontWeight: 800, margin: "14px 0 16px" }}>Le parcours d&rsquo;une loi</h1>
      <ol style={{ margin: 0, padding: "0 0 0 20px", display: "flex", flexDirection: "column", gap: 16 }}>
        {ETAPES.map((etape) => (
          <li key={etape.titre} style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--couleur-texte-secondaire)" }}>
            <strong style={{ color: "var(--couleur-texte)" }}>{etape.titre}.</strong> {etape.texte}
          </li>
        ))}
      </ol>
    </article>
  );
}
