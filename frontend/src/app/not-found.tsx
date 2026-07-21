import Link from "next/link";

export default function NotFound() {
  return (
    <div style={{ textAlign: "center", padding: "60px 0" }}>
      <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 12 }}>Page introuvable</h1>
      <p style={{ fontSize: 14.5, color: "var(--couleur-texte-faible)", marginBottom: 20 }}>
        Ce scrutin, ce député ou ce groupe n&rsquo;existe pas, ou plus.
      </p>
      <Link href="/" style={{ fontWeight: 600 }}>
        Retour à l&rsquo;accueil
      </Link>
    </div>
  );
}
