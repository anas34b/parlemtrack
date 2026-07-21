import Link from "next/link";

export default function Footer() {
  return (
    <footer style={{ borderTop: "1px solid var(--couleur-bordure)", marginTop: 40 }}>
      <nav
        aria-label="Pied de page"
        className="conteneur"
        style={{ padding: "20px", display: "flex", gap: 20, flexWrap: "wrap", fontSize: 13, color: "var(--couleur-texte-faible)" }}
      >
        <Link href="/">Accueil</Link>
        <Link href="/recherche">Recherche</Link>
        <Link href="/comprendre">Comprendre le Parlement</Link>
      </nav>
    </footer>
  );
}
