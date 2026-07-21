import { render, screen } from "@testing-library/react";
import PositionVote from "../PositionVote";

describe("PositionVote", () => {
  it("affiche le texte 'Pour' en plus de l'icône (jamais la couleur seule)", () => {
    render(<PositionVote position="pour" />);
    expect(screen.getByText("Pour")).toBeInTheDocument();
  });

  it("affiche le texte 'Contre'", () => {
    render(<PositionVote position="contre" />);
    expect(screen.getByText("Contre")).toBeInTheDocument();
  });

  it("affiche le texte 'Abstention'", () => {
    render(<PositionVote position="abstention" />);
    expect(screen.getByText("Abstention")).toBeInTheDocument();
  });

  it("affiche un libellé pour les positions non-votant", () => {
    render(<PositionVote position="nonVotant" />);
    expect(screen.getByText("Non-votant")).toBeInTheDocument();
  });

  it("inclut toujours une icône SVG à côté du texte", () => {
    const { container } = render(<PositionVote position="pour" />);
    expect(container.querySelector("svg")).toBeInTheDocument();
  });
});
