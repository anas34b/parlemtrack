import type { VoteParGroupe } from "@/types/api";

/**
 * Ligne "vote par groupe" : la barre est SEGMENTÉE par position (vert pour,
 * rouge contre, gris abstention/non-votant) ; la couleur du groupe n'apparaît
 * que sur la pastille à gauche, jamais sur la barre elle-même.
 */
export default function VoteParGroupeBarre({
  vote,
  couleurGroupe,
  largeurRelative,
}: {
  vote: VoteParGroupe;
  couleurGroupe: string | null;
  /** 0-100 : taille de la barre par rapport au groupe le plus nombreux. */
  largeurRelative: number;
}) {
  const total = vote.pour + vote.contre + vote.abstention + vote.non_votant || 1;
  const segments = [
    { valeur: vote.pour, couleur: "var(--couleur-pour)" },
    { valeur: vote.contre, couleur: "var(--couleur-contre)" },
    { valeur: vote.abstention, couleur: "var(--couleur-abstention)" },
    { valeur: vote.non_votant, couleur: "var(--couleur-nonvotant)" },
  ];
  const morceaux: string[] = [];
  if (vote.pour) morceaux.push(`${vote.pour} pour`);
  if (vote.contre) morceaux.push(`${vote.contre} contre`);
  if (vote.abstention) morceaux.push(`${vote.abstention} abst.`);
  if (vote.non_votant) morceaux.push(`${vote.non_votant} non-votant(s)`);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <div
        style={{
          width: 140,
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          gap: 7,
          fontSize: 12.5,
          fontWeight: 600,
          color: "var(--couleur-texte-secondaire)",
        }}
      >
        <span
          aria-hidden="true"
          style={{
            width: 9,
            height: 9,
            borderRadius: 3,
            background: couleurGroupe ?? "#9ca3af",
            flexShrink: 0,
          }}
        />
        <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {vote.groupe_nom}
        </span>
      </div>
      <div
        style={{
          flex: 1,
          height: 10,
          background: "var(--couleur-fond-secondaire)",
          borderRadius: 999,
          overflow: "hidden",
          display: "flex",
        }}
      >
        <div
          role="img"
          aria-label={`${vote.groupe_nom} : ${morceaux.join(", ")}`}
          style={{
            width: `${Math.max(4, largeurRelative)}%`,
            height: "100%",
            display: "flex",
            borderRadius: 999,
            overflow: "hidden",
          }}
        >
          {segments.map((segment, index) => (
            <div
              key={index}
              style={{
                width: `${(segment.valeur / total) * 100}%`,
                height: "100%",
                background: segment.couleur,
              }}
            />
          ))}
        </div>
      </div>
      <div
        style={{
          width: 130,
          flexShrink: 0,
          textAlign: "right",
          fontSize: 12,
          color: "var(--couleur-texte-faible)",
          fontWeight: 600,
        }}
      >
        {morceaux.join(" · ")}
      </div>
    </div>
  );
}
