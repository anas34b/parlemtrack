import Link from "next/link";
import type { Groupe } from "@/types/api";

/**
 * Nom du groupe avec pastille de couleur : la couleur n'est JAMAIS le seul
 * porteur d'information, le nom du groupe est toujours affiché en texte.
 */
export default function BadgeGroupe({ groupe }: { groupe: Groupe }) {
  return (
    <Link
      href={`/groupes/${groupe.id_an}`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 7,
        fontSize: 13.5,
        color: "#52525b",
        fontWeight: 600,
      }}
    >
      <span
        aria-hidden="true"
        style={{
          width: 9,
          height: 9,
          borderRadius: 3,
          background: groupe.couleur ?? "#9ca3af",
          flexShrink: 0,
        }}
      />
      {groupe.nom}
    </Link>
  );
}
