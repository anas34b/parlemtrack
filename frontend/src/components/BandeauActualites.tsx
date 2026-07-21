import { listerActualites } from "@/lib/api";

/** Bandeau de revue de presse (flux RSS collectés par le pipeline), affiché sur l'accueil. */
export default async function BandeauActualites() {
  let actualites;
  try {
    actualites = await listerActualites();
  } catch {
    return null;
  }
  if (actualites.length === 0) return null;

  const sources = [...new Map(actualites.map((a) => [a.source, a])).values()].slice(0, 4);

  return (
    <nav aria-label="Revue de presse" style={{ background: "var(--couleur-fond-secondaire)", borderBottom: "1px solid var(--couleur-bordure)" }}>
      <div
        className="conteneur"
        style={{
          padding: "8px 20px",
          display: "flex",
          alignItems: "center",
          gap: 10,
          flexWrap: "wrap",
          fontSize: 12.5,
          color: "var(--couleur-texte-faible)",
        }}
      >
        <span style={{ fontWeight: 600, color: "var(--couleur-texte-attenue)" }}>Revue de presse ·</span>
        {sources.map((actualite) => (
          <a
            key={actualite.lien}
            href={actualite.lien}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "var(--couleur-texte-attenue)", fontWeight: 500 }}
          >
            {actualite.titre} ({actualite.source})
          </a>
        ))}
      </div>
    </nav>
  );
}
