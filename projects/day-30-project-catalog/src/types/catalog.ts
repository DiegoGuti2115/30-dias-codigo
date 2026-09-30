export const catalogCategories = [
  "automation",
  "data",
  "monitoring",
  "utility",
  "security",
  "cloud-storage",
  "api",
  "cli",
  "configuration",
  "frontend",
  "ai",
  "ai-data",
  "ai-search",
  "ai-agents",
  "ai-quality",
  "full-stack",
  "portfolio",
] as const;

export type CatalogCategory = (typeof catalogCategories)[number];

export type CatalogProjectLink = Readonly<{
  label: string;
  href: string;
}>;

export type CatalogProject = Readonly<{
  id: string;
  day: number;
  name: string;
  summary: string;
  category: CatalogCategory;
  technologies: readonly string[];
  repositoryPath: string;
  links: readonly CatalogProjectLink[];
}>;

export type Catalog = Readonly<{
  version: 1;
  projects: readonly CatalogProject[];
}>;

export type CatalogLoadErrorCode = "invalid-data" | "read-error";

export type CatalogLoadSuccess = Readonly<{
  ok: true;
  catalog: Catalog;
}>;

export type CatalogLoadFailure = Readonly<{
  ok: false;
  code: CatalogLoadErrorCode;
  message: string;
}>;

export type CatalogLoadResult = CatalogLoadSuccess | CatalogLoadFailure;