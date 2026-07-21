import { render, screen } from "@testing-library/react";
import CarteScrutin from "../CarteScrutin";
import type { Scrutin } from "@/types/api";

function scrutin(overrides: Partial<Scrutin> = {}): Scrutin {
  return {
    uid: "VTA1",
    numero: 1,
    date_scrutin: "2026-07-20",
    titre: "Scrutin de test",
    type_vote: "scrutin public ordinaire",
    sort: "adopté",
    nb_pour: 10,
    nb_contre: 5,
    nb_abstention: 2,
    nb_non_votants: 1,
    lien_an: null,
    ...overrides,
  };
}

describe("CarteScrutin", () => {
  it("affiche le titre et les décomptes de voix", () => {
    render(<CarteScrutin scrutin={scrutin()} />);
    expect(screen.getByText("Scrutin de test")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("affiche le badge 'Adopté' pour un scrutin adopté", () => {
    render(<CarteScrutin scrutin={scrutin({ sort: "adopté" })} />);
    expect(screen.getByText("Adopté")).toBeInTheDocument();
  });

  it("affiche le badge 'Rejeté' pour un scrutin rejeté", () => {
    render(<CarteScrutin scrutin={scrutin({ sort: "rejeté" })} />);
    expect(screen.getByText("Rejeté")).toBeInTheDocument();
  });

  it("ne plante pas quand tous les décomptes sont à zéro (cas limite)", () => {
    render(<CarteScrutin scrutin={scrutin({ nb_pour: 0, nb_contre: 0, nb_abstention: 0 })} />);
    expect(screen.getByText("Scrutin de test")).toBeInTheDocument();
  });

  it("pointe vers la page de détail du scrutin", () => {
    render(<CarteScrutin scrutin={scrutin({ uid: "VTA42" })} />);
    expect(screen.getByRole("link")).toHaveAttribute("href", "/scrutins/VTA42");
  });
});
