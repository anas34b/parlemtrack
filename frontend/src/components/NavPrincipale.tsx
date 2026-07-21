"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LIENS = [
  { href: "/", label: "Accueil" },
  { href: "/scrutins", label: "Scrutins" },
  { href: "/deputes", label: "Députés" },
  { href: "/groupes", label: "Groupes" },
  { href: "/comprendre", label: "Comprendre" },
];

/**
 * Navigation principale : liens horizontaux en desktop, menu burger
 * accessible clavier en mobile (RGAA : aria-expanded, Échap pour fermer,
 * focus rendu au bouton à la fermeture).
 */
export default function NavPrincipale() {
  const pathname = usePathname();
  const [ouvert, setOuvert] = useState(false);
  const boutonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!ouvert) return;
    function surTouche(evenement: KeyboardEvent) {
      if (evenement.key === "Escape") {
        setOuvert(false);
        boutonRef.current?.focus();
      }
    }
    document.addEventListener("keydown", surTouche);
    return () => document.removeEventListener("keydown", surTouche);
  }, [ouvert]);

  function estActif(href: string) {
    return href === "/" ? pathname === "/" : pathname.startsWith(href);
  }

  return (
    <nav aria-label="Navigation principale">
      <ul className="nav-liens-desktop" style={{ listStyle: "none", display: "none", gap: 20, margin: 0, padding: 0 }}>
        {LIENS.map((lien) => (
          <li key={lien.href}>
            <Link
              href={lien.href}
              aria-current={estActif(lien.href) ? "page" : undefined}
              style={{
                fontSize: 14,
                fontWeight: 600,
                color: estActif(lien.href) ? "var(--couleur-texte)" : "var(--couleur-texte-attenue)",
              }}
            >
              {lien.label}
            </Link>
          </li>
        ))}
      </ul>

      <button
        ref={boutonRef}
        type="button"
        className="nav-bouton-burger"
        aria-expanded={ouvert}
        aria-controls="menu-mobile"
        aria-label={ouvert ? "Fermer le menu" : "Ouvrir le menu"}
        onClick={() => setOuvert((valeur) => !valeur)}
        style={{
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          width: 38,
          height: 38,
          border: "1px solid var(--couleur-bordure)",
          borderRadius: 10,
          background: "var(--couleur-carte)",
        }}
      >
        <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none">
          {ouvert ? (
            <path d="M6 6l12 12M18 6L6 18" stroke="#18181b" strokeWidth="2.2" strokeLinecap="round" />
          ) : (
            <path d="M4 7h16M4 12h16M4 17h16" stroke="#18181b" strokeWidth="2.2" strokeLinecap="round" />
          )}
        </svg>
      </button>

      {ouvert && (
        <ul
          id="menu-mobile"
          className="nav-liens-mobile"
          style={{
            listStyle: "none",
            margin: 0,
            padding: "10px 20px 16px",
            display: "flex",
            flexDirection: "column",
            gap: 4,
            borderTop: "1px solid var(--couleur-bordure)",
            background: "var(--couleur-carte)",
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
          }}
        >
          {LIENS.map((lien) => (
            <li key={lien.href}>
              <Link
                href={lien.href}
                aria-current={estActif(lien.href) ? "page" : undefined}
                onClick={() => setOuvert(false)}
                style={{
                  display: "block",
                  padding: "10px 4px",
                  fontSize: 15,
                  fontWeight: 600,
                  color: estActif(lien.href) ? "var(--couleur-texte)" : "var(--couleur-texte-attenue)",
                }}
              >
                {lien.label}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </nav>
  );
}
