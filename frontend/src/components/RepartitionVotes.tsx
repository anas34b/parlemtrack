/**
 * Barre segmentée pour/contre/abstention d'un scrutin (vue d'ensemble).
 * Purement décorative : les chiffres exacts sont toujours affichés en texte à côté.
 */
export default function RepartitionVotes({
  pour,
  contre,
  abstention,
}: {
  pour: number;
  contre: number;
  abstention: number;
}) {
  const total = pour + contre + abstention || 1;
  return (
    <div
      role="img"
      aria-label={`Répartition des voix : ${pour} pour, ${contre} contre, ${abstention} abstention`}
      style={{
        display: "flex",
        height: 8,
        borderRadius: 999,
        overflow: "hidden",
        background: "var(--couleur-fond-secondaire)",
      }}
    >
      <div style={{ width: `${(pour / total) * 100}%`, background: "var(--couleur-pour)" }} />
      <div style={{ width: `${(contre / total) * 100}%`, background: "var(--couleur-contre)" }} />
      <div
        style={{ width: `${(abstention / total) * 100}%`, background: "var(--couleur-abstention)" }}
      />
    </div>
  );
}
