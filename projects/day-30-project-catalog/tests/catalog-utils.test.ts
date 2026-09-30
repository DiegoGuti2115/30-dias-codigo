import { describe, expect, it } from "vitest";

import {
  filterCatalogProjects,
  getCatalogCategories,
  getCatalogTechnologies,
  initialCatalogFilters,
} from "@/features/catalog/catalog-utils";
import { loadLocalCatalog } from "@/lib/catalog-source";

const localCatalog = loadLocalCatalog();

if (!localCatalog.ok) {
  throw new Error("Expected the local catalog fixture to be available for filter tests.");
}

const { projects } = localCatalog.catalog;

describe("catalog filtering", () => {
  it("finds projects across name, summary, category, and technology", () => {
    expect(filterCatalogProjects(projects, { ...initialCatalogFilters, query: "FastAPI" })).toHaveLength(5);
    expect(filterCatalogProjects(projects, { ...initialCatalogFilters, query: "contraseñas" })[0]?.id).toBe(
      "day-06-password-policy-checker",
    );
  });

  it("combines query, category, and technology criteria", () => {
    const results = filterCatalogProjects(projects, {
      query: "dashboard",
      category: "frontend",
      technology: "Next.js",
    });

    expect(results.map(({ id }) => id)).toEqual(["day-21-dashboard-metrics"]);
  });

  it("normalizes surrounding query whitespace without mutating the original collection", () => {
    const originalProjectIds = projects.map((project) => project.id);
    const results = filterCatalogProjects(projects, { ...initialCatalogFilters, query: "  pomodoro  " });

    expect(results.map((project) => project.id)).toEqual(["day-16-pomodoro-timer"]);
    expect(projects.map((project) => project.id)).toEqual(originalProjectIds);
  });

  it("returns an empty collection when criteria do not match", () => {
    expect(filterCatalogProjects(projects, { ...initialCatalogFilters, technology: "Rust" })).toEqual([]);
  });

  it("derives deterministic unique filter options", () => {
    const categories = getCatalogCategories(projects);
    const technologies = getCatalogTechnologies(projects);

    expect(categories).toContain("frontend");
    expect(technologies).toContain("Next.js");
    expect(technologies).toHaveLength(new Set(technologies).size);
    expect(categories).toEqual([...categories].sort((left, right) => left.localeCompare(right, "es")));
    expect(technologies).toEqual([...technologies].sort((left, right) => left.localeCompare(right, "es")));
  });
});