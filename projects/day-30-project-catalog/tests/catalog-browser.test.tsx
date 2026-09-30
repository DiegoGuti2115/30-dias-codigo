import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CatalogBrowser } from "@/features/catalog/catalog-browser";
import { loadLocalCatalog } from "@/lib/catalog-source";

const localCatalog = loadLocalCatalog();

if (!localCatalog.ok) {
  throw new Error("Expected the local catalog fixture to be available for browser tests.");
}

describe("catalog browser", () => {
  it("connects every filter with instructions and the announced result count", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    const filterHelp = screen.getByText("Los resultados se actualizan al escribir o seleccionar un criterio.");
    const resultCount = screen.getByRole("status");

    expect(filterHelp.getAttribute("id")).toBe("catalog-filter-help");
    expect(resultCount.getAttribute("id")).toBe("catalog-result-count");
    expect(resultCount.textContent).toBe("30 proyectos encontrados");
    expect(resultCount.getAttribute("aria-atomic")).toBe("true");

    for (const control of [
      screen.getByRole("searchbox", { name: "Buscar proyectos" }),
      screen.getByRole("combobox", { name: "Categoría" }),
      screen.getByRole("combobox", { name: "Tecnología" }),
    ]) {
      expect(control.getAttribute("aria-describedby")).toBe("catalog-filter-help catalog-result-count");
    }
  });

  it("filters projects by a text query and announces the result count", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    fireEvent.change(screen.getByRole("searchbox", { name: "Buscar proyectos" }), {
      target: { value: "Pomodoro" },
    });

    expect(screen.getByText("1 proyecto encontrado")).toBeTruthy();
    expect(screen.getByRole("heading", { level: 3, name: "Temporizador Pomodoro" })).toBeTruthy();
  });

  it("marks the results region as busy only while deferred filters are updating", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    expect(screen.getByRole("region", { name: "Resultados del catálogo" }).getAttribute("aria-busy")).toBe("false");
  });

  it("combines category and technology filters", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    fireEvent.change(screen.getByRole("combobox", { name: "Categoría" }), { target: { value: "frontend" } });
    fireEvent.change(screen.getByRole("combobox", { name: "Tecnología" }), { target: { value: "Next.js" } });

    expect(screen.getByText("2 proyectos encontrados")).toBeTruthy();
    expect(screen.getByRole("heading", { level: 3, name: "Dashboard de métricas" })).toBeTruthy();
    expect(screen.getByRole("heading", { level: 3, name: "Playground de cliente API" })).toBeTruthy();
  });

  it("shows no results and restores the complete collection", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    fireEvent.change(screen.getByRole("searchbox", { name: "Buscar proyectos" }), {
      target: { value: "inexistente" },
    });

    expect(screen.getByRole("heading", { level: 3, name: "No encontramos proyectos con esos criterios" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Ver todos los proyectos" }));

    expect(screen.getByText("30 proyectos encontrados")).toBeTruthy();
    expect(screen.queryByRole("heading", { level: 3, name: "No encontramos proyectos con esos criterios" })).toBeNull();
  });

  it("keeps the reset control unavailable until a criterion is active", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    const resetButton = screen.getByRole("button", { name: "Restablecer criterios" }) as HTMLButtonElement;
    expect(resetButton.disabled).toBe(true);

    fireEvent.change(screen.getByRole("searchbox", { name: "Buscar proyectos" }), { target: { value: "API" } });
    expect(resetButton.disabled).toBe(false);
  });

  it("resets every active filter with the dedicated control", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    const searchInput = screen.getByRole("searchbox", { name: "Buscar proyectos" });
    fireEvent.change(searchInput, { target: { value: "API" } });
    fireEvent.change(screen.getByRole("combobox", { name: "Categoría" }), { target: { value: "api" } });
    fireEvent.click(screen.getByRole("button", { name: "Restablecer criterios" }));

    expect((searchInput as HTMLInputElement).value).toBe("");
    expect((screen.getByRole("combobox", { name: "Categoría" }) as HTMLSelectElement).value).toBe("");
    expect(screen.getByText("30 proyectos encontrados")).toBeTruthy();
  });

  it("supports keyboard changes on native filter controls", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    const categoryFilter = screen.getByRole("combobox", { name: "Categoría" });
    categoryFilter.focus();
    fireEvent.keyDown(categoryFilter, { key: "ArrowDown" });
    fireEvent.change(categoryFilter, { target: { value: "api" } });

    expect(document.activeElement).toBe(categoryFilter);
    expect(screen.getByText("4 proyectos encontrados")).toBeTruthy();
  });

  it("marks the no-results state as an announced status and preserves a keyboard recovery path", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    fireEvent.change(screen.getByRole("searchbox", { name: "Buscar proyectos" }), {
      target: { value: "inexistente" },
    });

    const noResults = screen.getByRole("status", { name: "No encontramos proyectos con esos criterios" });
    const recovery = screen.getByRole("button", { name: "Ver todos los proyectos" });
    recovery.focus();

    expect(noResults.getAttribute("aria-live")).toBe("polite");
    expect(document.activeElement).toBe(recovery);

    fireEvent.click(recovery);
    expect(screen.getByText("30 proyectos encontrados")).toBeTruthy();
  });

  it("renders validated GitHub project links", () => {
    render(<CatalogBrowser projects={localCatalog.catalog.projects} />);

    const projectLinks = screen.getAllByRole("link", { name: "Código" });
    expect(projectLinks[0]?.getAttribute("href")).toBe(
      "https://github.com/DiegoGuti2115/30-dias-codigo/tree/main/projects/day-01-download-sorter",
    );
    expect(projectLinks).toHaveLength(30);
    expect(
      projectLinks.every((link) =>
        link.getAttribute("href")?.startsWith("https://github.com/DiegoGuti2115/30-dias-codigo/tree/main/projects/"),
      ),
    ).toBe(true);
  });
});