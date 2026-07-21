import Link from "next/link";
import NavPrincipale from "@/components/NavPrincipale";

/** En-tête collant : logo, navigation, recherche (formulaire GET, sans JS requis). */
export default function Header() {
  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 10,
        background: "rgba(255,255,255,0.92)",
        backdropFilter: "blur(8px)",
        borderBottom: "1px solid var(--couleur-bordure)",
      }}
    >
      <div
        className="conteneur"
        style={{ padding: "14px 20px", display: "flex", alignItems: "center", gap: 20 }}
      >
        <Link
          href="/"
          style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0, color: "inherit" }}
        >
          <span
            aria-hidden="true"
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: "#18181b",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path d="M4 19V10M12 19V5M20 19V13" stroke="#fafafa" strokeWidth="2.4" strokeLinecap="round" />
            </svg>
          </span>
          <span style={{ fontWeight: 700, fontSize: 16, letterSpacing: "-0.01em" }}>ParlemTrack</span>
        </Link>
        <NavPrincipale />
        <form
          action="/recherche"
          method="get"
          role="search"
          style={{ flex: 1, maxWidth: 280, marginLeft: "auto" }}
        >
          <label
            htmlFor="recherche-globale"
            style={{ position: "absolute", width: 1, height: 1, overflow: "hidden", clipPath: "inset(50%)" }}
          >
            Rechercher un scrutin, un député, un groupe
          </label>
          <input
            id="recherche-globale"
            name="q"
            type="search"
            placeholder="Rechercher un scrutin, un député..."
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "9px 14px",
              borderRadius: 10,
              border: "1px solid var(--couleur-bordure)",
              background: "var(--couleur-fond-secondaire)",
              fontSize: 14,
              color: "var(--couleur-texte)",
              fontFamily: "inherit",
            }}
          />
        </form>
      </div>
    </header>
  );
}
