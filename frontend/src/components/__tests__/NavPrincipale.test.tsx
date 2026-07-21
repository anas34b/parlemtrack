import { render, screen, fireEvent } from "@testing-library/react";
import NavPrincipale from "../NavPrincipale";

jest.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

describe("NavPrincipale", () => {
  it("affiche les 5 liens de navigation", () => {
    render(<NavPrincipale />);
    for (const label of ["Accueil", "Scrutins", "Députés", "Groupes", "Comprendre"]) {
      expect(screen.getAllByText(label).length).toBeGreaterThan(0);
    }
  });

  it("le menu burger est fermé par défaut puis s'ouvre au clic, avec aria-expanded à jour", () => {
    render(<NavPrincipale />);
    const bouton = screen.getByRole("button", { name: /ouvrir le menu/i, hidden: true });
    expect(bouton).toHaveAttribute("aria-expanded", "false");
    expect(document.getElementById("menu-mobile")).not.toBeInTheDocument();

    fireEvent.click(bouton);
    expect(bouton).toHaveAttribute("aria-expanded", "true");
    expect(document.getElementById("menu-mobile")).toBeInTheDocument();
  });

  it("la touche Échap referme le menu et rend le focus au bouton", () => {
    render(<NavPrincipale />);
    const bouton = screen.getByRole("button", { name: /ouvrir le menu/i, hidden: true });
    fireEvent.click(bouton);
    expect(document.getElementById("menu-mobile")).toBeInTheDocument();

    fireEvent.keyDown(document, { key: "Escape" });
    expect(document.getElementById("menu-mobile")).not.toBeInTheDocument();
    expect(bouton).toHaveFocus();
  });
});
