import { describe, expect, it } from "vitest";

import { normalizeCatalogData } from "@/lib/catalog-schema";
import { loadCatalogFromData, loadCatalogFromLoader, loadLocalCatalog } from "@/lib/catalog-source";

const validCatalog = {
  version: 1,
  projects: [
    {
      id: "day-01-download-sorter",
      day: 1,
      name: "Clasificador de descargas",
      summary: "Organiza archivos descargados por tipo.",
      category: "automation",
      technologies: ["Python"],
      repositoryPath: "../day-01-download-sorter",
      links: [
        {
          label: "Código",
          href: "https://github.com/DiegoGuti2115/30-dias-codigo/tree/main/projects/day-01-download-sorter",
        },
      ],
    },
  ],
};

describe("catalog contract", () => {
  it("normalizes a valid catalog with a trusted GitHub project link into the domain model", () => {
    const catalog = normalizeCatalogData(validCatalog);

    expect(catalog.projects).toHaveLength(1);
    expect(catalog.projects[0]).toMatchObject({
      id: "day-01-download-sorter",
      day: 1,
      category: "automation",
    });
  });

  it.each([
    ["duplicate project ids", { ...validCatalog, projects: [validCatalog.projects[0], validCatalog.projects[0]] }],
    [
      "a day that does not match the identifier",
      { ...validCatalog, projects: [{ ...validCatalog.projects[0], day: 2 }] },
    ],
    [
      "a link outside the configured GitHub repository",
      {
        ...validCatalog,
        projects: [{ ...validCatalog.projects[0], links: [{ label: "Código", href: "https://example.com" }] }],
      },
    ],
    [
      "a GitHub link that does not target a project directory",
      {
        ...validCatalog,
        projects: [
          {
            ...validCatalog.projects[0],
            links: [{ label: "Código", href: "https://github.com/DiegoGuti2115/30-dias-codigo/blob/main/README.md" }],
          },
        ],
      },
    ],
    [
      "duplicate technologies",
      { ...validCatalog, projects: [{ ...validCatalog.projects[0], technologies: ["Python", "Python"] }] },
    ],
    [
      "a repository path that does not belong to its project",
      { ...validCatalog, projects: [{ ...validCatalog.projects[0], repositoryPath: "../day-02-clipboard-manager" }] },
    ],
    [
      "an unexpected field at the catalog boundary",
      { ...validCatalog, source: "untrusted" },
    ],
  ])("rejects %s", (_scenario, invalidCatalog) => {
    expect(() => normalizeCatalogData(invalidCatalog)).toThrow();
  });
});

describe("catalog source", () => {
  it("loads the versioned local fallback catalog", () => {
    const result = loadLocalCatalog();

    expect(result).toMatchObject({ ok: true });

    if (result.ok) {
      expect(result.catalog.projects).toHaveLength(30);
      expect(result.catalog.projects.at(-1)?.id).toBe("day-30-project-catalog");
    }
  });

  it("preserves the complete local series and matching GitHub destinations in ascending day order", () => {
    const result = loadLocalCatalog();

    if (!result.ok) {
      throw new Error("Expected the local catalog fixture to be available for regression tests.");
    }

    expect(result.catalog.projects.map((project) => project.day)).toEqual(Array.from({ length: 30 }, (_, index) => index + 1));
    expect(result.catalog.projects.every((project) => project.links.every((link) => link.href === `https://github.com/DiegoGuti2115/30-dias-codigo/tree/main/projects/${project.id}`))).toBe(true);
  });

  it("returns an explicit invalid-data result instead of partially loading an invalid catalog", () => {
    const result = loadCatalogFromData({ version: 1, projects: [] });

    expect(result).toEqual({
      ok: false,
      code: "invalid-data",
      message: "The local project catalog could not be validated.",
    });
  });

  it("returns a read error when the data loader throws", () => {
    const result = loadCatalogFromLoader(() => {
      throw new Error("Fixture is unavailable");
    });

    expect(result).toEqual({
      ok: false,
      code: "read-error",
      message: "The local project catalog could not be read.",
    });
  });
});