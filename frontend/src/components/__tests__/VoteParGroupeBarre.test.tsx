import { render, screen } from "@testing-library/react";
import VoteParGroupeBarre from "../VoteParGroupeBarre";
import type { VoteParGroupe } from "@/types/api";

function vote(overrides: Partial<VoteParGroupe> = {}): VoteParGroupe {
  return {
    groupe_id: "PO1",
    groupe_nom: "Groupe Test",
    pour: 10,
    contre: 3,
    abstention: 1,
    non_votant: 0,
    ...overrides,
  };
}

describe("VoteParGroupeBarre", () => {
  it("affiche le nom du groupe et le détail des voix", () => {
    render(<VoteParGroupeBarre vote={vote()} couleurGroupe="#123456" largeurRelative={100} />);
    expect(screen.getByText("Groupe Test")).toBeInTheDocument();
    expect(screen.getByText(/10 pour/)).toBeInTheDocument();
    expect(screen.getByText(/3 contre/)).toBeInTheDocument();
  });

  it("n'affiche pas de segment à zéro dans le détail texte", () => {
    render(<VoteParGroupeBarre vote={vote({ contre: 0, abstention: 0 })} couleurGroupe="#123456" largeurRelative={50} />);
    expect(screen.queryByText(/contre/)).not.toBeInTheDocument();
  });

  it("utilise une couleur neutre par défaut si le groupe n'a pas de couleur (cas limite)", () => {
    const { container } = render(
      <VoteParGroupeBarre vote={vote()} couleurGroupe={null} largeurRelative={100} />
    );
    const pastille = container.querySelector('span[aria-hidden="true"]');
    expect(pastille).toHaveStyle({ background: "#9ca3af" });
  });
});
