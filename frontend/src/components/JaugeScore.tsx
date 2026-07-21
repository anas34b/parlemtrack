/** Jauge de score (participation, loyauté...) en pourcentage. */
export default function JaugeScore({
  label,
  valeur,
  couleur = "#18181b",
}: {
  label: string;
  /** Score de 0 à 1 (ex. 0.92), ou null si non disponible. */
  valeur: number | null;
  couleur?: string;
}) {
  const pourcentage = valeur !== null ? Math.round(valeur * 100) : null;
  return (
    <div
      style={{
        background: "var(--couleur-carte)",
        border: "1px solid var(--couleur-bordure)",
        borderRadius: "var(--rayon-carte)",
        padding: 18,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 9 }}>
        <span style={{ fontSize: 12.5, fontWeight: 600, color: "var(--couleur-texte-attenue)" }}>
          {label}
        </span>
        <span style={{ fontSize: 13, fontWeight: 800 }}>
          {pourcentage !== null ? `${pourcentage}%` : "N/A"}
        </span>
      </div>
      <div
        style={{
          height: 9,
          background: "var(--couleur-fond-secondaire)",
          borderRadius: 999,
          overflow: "hidden",
        }}
        role="img"
        aria-label={`${label} : ${pourcentage !== null ? `${pourcentage} %` : "donnée non disponible"}`}
      >
        <div
          style={{
            height: "100%",
            width: `${pourcentage ?? 0}%`,
            background: couleur,
            borderRadius: 999,
          }}
        />
      </div>
    </div>
  );
}
