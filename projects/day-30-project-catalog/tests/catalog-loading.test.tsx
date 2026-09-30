import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Loading from "@/app/loading";

describe("catalog loading state", () => {
  it("reserves an accessible busy state with non-interactive project previews", () => {
    render(<Loading />);

    const main = screen.getByRole("main", { busy: true });
    const status = screen.getByRole("status");

    expect(main.getAttribute("aria-labelledby")).toBe("loading-catalog-title");
    expect(screen.getByRole("heading", { level: 1, name: "Cargando el catálogo de proyectos" })).toBeTruthy();
    expect(status.textContent).toBe("Estamos preparando los proyectos para que puedas explorarlos.");
    expect(screen.getAllByLabelText("Vista previa de tarjeta de proyecto")).toHaveLength(3);
  });
});