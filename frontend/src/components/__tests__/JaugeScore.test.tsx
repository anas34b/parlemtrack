import { render, screen } from "@testing-library/react";
import JaugeScore from "../JaugeScore";

describe("JaugeScore", () => {
  it("affiche le pourcentage arrondi", () => {
    render(<JaugeScore label="Participation" valeur={0.923} />);
    expect(screen.getByText("92%")).toBeInTheDocument();
    expect(screen.getByText("Participation")).toBeInTheDocument();
  });

  it("affiche 'N/A' quand la donnée est absente (cas limite)", () => {
    render(<JaugeScore label="Loyauté" valeur={null} />);
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });

  it("expose un rôle image avec un libellé accessible", () => {
    render(<JaugeScore label="Participation" valeur={0.5} />);
    expect(screen.getByRole("img", { name: /Participation : 50 %/ })).toBeInTheDocument();
  });
});
