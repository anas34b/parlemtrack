/** Badge affiché sur un député dont le mandat a pris fin en cours de législature. */
export default function BadgeMandatTermine() {
  return (
    <span
      style={{
        fontSize: 11,
        fontWeight: 700,
        padding: "3px 9px",
        borderRadius: 999,
        background: "#f4f4f5",
        color: "#52525b",
        border: "1px solid #e4e4e7",
      }}
    >
      Mandat terminé
    </span>
  );
}
