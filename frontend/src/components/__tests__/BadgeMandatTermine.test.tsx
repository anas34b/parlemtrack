import { render, screen } from "@testing-library/react";
import BadgeMandatTermine from "../BadgeMandatTermine";

describe("BadgeMandatTermine", () => {
  it("affiche le texte 'Mandat terminé'", () => {
    render(<BadgeMandatTermine />);
    expect(screen.getByText("Mandat terminé")).toBeInTheDocument();
  });
});
