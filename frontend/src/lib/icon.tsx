import { ImageResponse } from "next/og";

/** Icône PWA générée dynamiquement (logo ParlemTrack), à une taille donnée. */
export function genererIcone(taille: number): ImageResponse {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#18181b",
          borderRadius: taille * 0.2,
        }}
      >
        <svg width={taille * 0.55} height={taille * 0.55} viewBox="0 0 24 24" fill="none">
          <path
            d="M4 19V10M12 19V5M20 19V13"
            stroke="#fafafa"
            strokeWidth="2.4"
            strokeLinecap="round"
          />
        </svg>
      </div>
    ),
    { width: taille, height: taille }
  );
}
