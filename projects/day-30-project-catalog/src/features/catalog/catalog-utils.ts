import type { CatalogProject } from "@/types/catalog";

export type CatalogFilters = Readonly<{
  query: string;
  category: string;
  technology: string;
}>;

export const initialCatalogFilters: CatalogFilters = {
  query: "",
  category: "",
  technology: "",
};

export function filterCatalogProjects(
  projects: readonly CatalogProject[],
  filters: CatalogFilters,
): readonly CatalogProject[] {
  const query = filters.query.trim().toLocaleLowerCase("es");
  const category = filters.category.trim();
  const technology = filters.technology.trim();

  return projects.filter((project) => {
    const searchableProject = [project.name, project.summary, project.category, ...project.technologies]
      .join(" ")
      .toLocaleLowerCase("es");

    return (
      (!query || searchableProject.includes(query)) &&
      (!category || project.category === category) &&
      (!technology || project.technologies.includes(technology))
    );
  });
}

export function getCatalogCategories(projects: readonly CatalogProject[]): readonly string[] {
  return [...new Set(projects.map((project) => project.category))].sort((left, right) => left.localeCompare(right, "es"));
}

export function getCatalogTechnologies(projects: readonly CatalogProject[]): readonly string[] {
  return [...new Set(projects.flatMap((project) => project.technologies))].sort((left, right) =>
    left.localeCompare(right, "es"),
  );
}

export function hasActiveCatalogFilters(filters: CatalogFilters): boolean {
  return Boolean(filters.query.trim() || filters.category || filters.technology);
}

export function formatCatalogCategory(category: string): string {
  return category.replaceAll("-", " ");
}