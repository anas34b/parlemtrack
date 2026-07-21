/** Badge "Adopté" / "Rejeté" à partir du champ `sort` du scrutin. */
export default function BadgeStatutScrutin({ sort }: { sort: string }) {
  const adopte = sort.toLowerCase().includes("adopt");
  return (
    <span
      style={{
        fontSize: 12,
        fontWeight: 700,
        padding: "3px 10px",
        borderRadius: 999,
        background: adopte ? "#f0fdf4" : "#fef2f2",
        color: adopte ? "#047857" : "#b91c1c",
        whiteSpace: "nowrap",
      }}
    >
      {adopte ? "Adopté" : "Rejeté"}
    </span>
  );
}
