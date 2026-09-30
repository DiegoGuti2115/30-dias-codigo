import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { metadata } from "@/app/layout";
import HomePage from "@/app/page";
import { CatalogState } from "@/components/catalog-state";

function getMainContent() {
  const mainContent = document.querySelector("main");

  if (!mainContent) {
    throw new Error("Expected the catalog main landmark to be rendered.");
  }

  return mainContent;
}

describe("catalog presentation", () => {
  it("describes the delivered catalog with production metadata", () => {
    expect(metadata.title).toBe("Catálogo de proyectos | 30 Días, 30 Proyectos");
    expect(metadata.description).toContain("30 proyectos");
    expect(metadata.applicationName).toBe("Catálogo de proyectos");
    expect(metadata.robots).toEqual({ index: true, follow: true });
  });

  it("renders the static catalog hierarchy with semantic landmarks and a skip link", () => {
    render(<HomePage />);

    expect(screen.getByRole("link", { name: "Saltar al contenido principal" }).getAttribute("href")).toBe(
      "#catalog-content",
    );
    expect(screen.getByRole("heading", { level: 1, name: "Una colección para recorrer todo lo construido." })).toBeTruthy();
    expect(screen.getByRole("heading", { level: 2, name: "Encuentra el proyecto que necesitas" })).toBeTruthy();
    expect(getMainContent().getAttribute("id")).toBe("catalog-content");
  });

  it("presents the complete catalog with GitHub project links", () => {
    render(<HomePage />);

    expect(screen.getAllByRole("article")).toHaveLength(30);
    expect(screen.getByRole("heading", { level: 3, name: "Clasificador de descargas" })).toBeTruthy();
    expect(screen.getAllByText("Python")).toHaveLength(13);
    expect(screen.getAllByRole("link", { name: "Código" })).toHaveLength(30);
  });

  it.each(["loading", "empty", "error"] as const)("renders the accessible %s state", (kind) => {
    render(<CatalogState kind={kind} />);

    expect(screen.getByRole("region", { name: /cargando|aún no hay|no se pudo/i })).toBeTruthy();
    expect(screen.getByRole("heading", { level: 2 })).toBeTruthy();
  });
});