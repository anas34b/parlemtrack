import type { AnalyseIA } from "@/types/api";

const STYLES: Record<AnalyseIA["coherence_macro"], { label: string; bg: string; texte: string }> = {
  aligne: { label: "Aligné", bg: "#f0fdf4", texte: "#047857" },
  mitige: { label: "Mitigé", bg: "#fffbeb", texte: "#b45309" },
  contradictoire: { label: "Contradictoire", bg: "#fdf2f8", texte: "#be185d" },
};

/** Badge de cohérence macro-économique de l'analyse IA. */
export default function BadgeCoherence({ coherence }: { coherence: AnalyseIA["coherence_macro"] }) {
  const style = STYLES[coherence];
  return (
    <span
      style={{
        fontSize: 11.5,
        fontWeight: 700,
        padding: "3px 10px",
        borderRadius: 999,
        background: style.bg,
        color: style.texte,
      }}
    >
      Cohérence macro : {style.label}
    </span>
  );
}
