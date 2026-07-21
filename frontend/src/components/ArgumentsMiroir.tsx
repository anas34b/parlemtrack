/**
 * Colonnes "Arguments pour" / "Arguments contre" parfaitement symétriques :
 * même structure, même style, même largeur, une seule différence de couleur.
 */
export default function ArgumentsMiroir({
  argumentsPour,
  argumentsContre,
}: {
  argumentsPour: string[];
  argumentsContre: string[];
}) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
      <section
        aria-labelledby="titre-arguments-pour"
        style={{ border: "1px solid #dcfce7", background: "#f0fdf4", borderRadius: 12, padding: 16 }}
      >
        <h3
          id="titre-arguments-pour"
          style={{
            fontSize: 12.5,
            fontWeight: 700,
            color: "#047857",
            margin: "0 0 10px",
            textTransform: "uppercase",
            letterSpacing: "0.03em",
          }}
        >
          Arguments pour
        </h3>
        <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
          {argumentsPour.map((argument, index) => (
            <li
              key={index}
              style={{ display: "flex", gap: 8, marginBottom: 9, fontSize: 13, lineHeight: 1.5, color: "#14532d" }}
            >
              <svg
                aria-hidden="true"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                style={{ flexShrink: 0, marginTop: 3 }}
              >
                <path d="M12 5v14M5 12h14" stroke="#047857" strokeWidth="2.6" strokeLinecap="round" />
              </svg>
              <span>{argument}</span>
            </li>
          ))}
        </ul>
      </section>
      <section
        aria-labelledby="titre-arguments-contre"
        style={{ border: "1px solid #fee2e2", background: "#fef2f2", borderRadius: 12, padding: 16 }}
      >
        <h3
          id="titre-arguments-contre"
          style={{
            fontSize: 12.5,
            fontWeight: 700,
            color: "#b91c1c",
            margin: "0 0 10px",
            textTransform: "uppercase",
            letterSpacing: "0.03em",
          }}
        >
          Arguments contre
        </h3>
        <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
          {argumentsContre.map((argument, index) => (
            <li
              key={index}
              style={{ display: "flex", gap: 8, marginBottom: 9, fontSize: 13, lineHeight: 1.5, color: "#7f1d1d" }}
            >
              <svg
                aria-hidden="true"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                style={{ flexShrink: 0, marginTop: 3 }}
              >
                <path d="M5 12h14" stroke="#b91c1c" strokeWidth="2.6" strokeLinecap="round" />
              </svg>
              <span>{argument}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
