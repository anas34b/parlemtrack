import type { PositionVote as PositionVoteType } from "@/types/api";

const META: Record<
  PositionVoteType,
  { label: string; couleur: string; icone: React.ReactNode }
> = {
  pour: {
    label: "Pour",
    couleur: "#059669",
    icone: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M20 6L9 17l-5-5"
          stroke="#059669"
          strokeWidth="2.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  contre: {
    label: "Contre",
    couleur: "#dc2626",
    icone: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M18 6L6 18M6 6l12 12" stroke="#dc2626" strokeWidth="2.6" strokeLinecap="round" />
      </svg>
    ),
  },
  abstention: {
    label: "Abstention",
    couleur: "#71717a",
    icone: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M5 12h14" stroke="#71717a" strokeWidth="2.6" strokeLinecap="round" />
      </svg>
    ),
  },
  nonVotant: {
    label: "Non-votant",
    couleur: "#a1a1aa",
    icone: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="8" stroke="#a1a1aa" strokeWidth="2" strokeDasharray="3 3" />
      </svg>
    ),
  },
  nonVotantVolontaire: {
    label: "Non-votant volontaire",
    couleur: "#a1a1aa",
    icone: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="8" stroke="#a1a1aa" strokeWidth="2" strokeDasharray="3 3" />
      </svg>
    ),
  },
};

/**
 * Position de vote : toujours icône + texte, jamais la couleur seule (RGAA).
 */
export default function PositionVote({ position }: { position: PositionVoteType }) {
  const meta = META[position];
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        fontSize: 12.5,
        fontWeight: 700,
        color: meta.couleur,
        whiteSpace: "nowrap",
      }}
    >
      {meta.icone}
      {meta.label}
    </span>
  );
}
