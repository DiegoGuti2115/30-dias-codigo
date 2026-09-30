"use client";

import { useDeferredValue, useMemo, useState } from "react";

import { CatalogCard } from "@/features/catalog/catalog-card";
import {
  filterCatalogProjects,
  formatCatalogCategory,
  getCatalogCategories,
  getCatalogTechnologies,
  hasActiveCatalogFilters,
  initialCatalogFilters,
  type CatalogFilters,
} from "@/features/catalog/catalog-utils";
import type { CatalogProject } from "@/types/catalog";

type CatalogBrowserProperties = Readonly<{
  projects: readonly CatalogProject[];
}>;

export function CatalogBrowser({ projects }: CatalogBrowserProperties) {
  const [filters, setFilters] = useState<CatalogFilters>(initialCatalogFilters);
  const deferredFilters = useDeferredValue(filters);
  const categories = useMemo(() => getCatalogCategories(projects), [projects]);
  const technologies = useMemo(() => getCatalogTechnologies(projects), [projects]);
  const visibleProjects = useMemo(() => filterCatalogProjects(projects, deferredFilters), [projects, deferredFilters]);
  const hasActiveFilters = hasActiveCatalogFilters(filters);
  const isUpdatingResults = filters !== deferredFilters;

  function updateFilter<Key extends keyof CatalogFilters>(key: Key, value: CatalogFilters[Key]) {
    setFilters((currentFilters) => ({ ...currentFilters, [key]: value }));
  }

  return (
    <section className="catalog-browser" aria-labelledby="catalog-browser-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Explora la colección</p>
          <h2 id="catalog-browser-title">Encuentra el proyecto que necesitas</h2>
        </div>
        <p>Combina texto, categoría y tecnología para recorrer las treinta entregas de la mini-serie.</p>
      </div>

      <form className="catalog-controls" aria-describedby="catalog-filter-help" onSubmit={(event) => event.preventDefault()}>
        <p id="catalog-filter-help" className="filter-help">
          Los resultados se actualizan al escribir o seleccionar un criterio.
        </p>
        <div className="search-field">
          <label htmlFor="project-search">Buscar proyectos</label>
          <input
            id="project-search"
            type="search"
            value={filters.query}
            onChange={(event) => updateFilter("query", event.target.value)}
            placeholder="Nombre, tecnología o categoría"
            aria-describedby="catalog-filter-help catalog-result-count"
          />
        </div>
        <div className="filter-field">
          <label htmlFor="category-filter">Categoría</label>
          <select
            id="category-filter"
            value={filters.category}
            onChange={(event) => updateFilter("category", event.target.value)}
            aria-describedby="catalog-filter-help catalog-result-count"
          >
            <option value="">Todas las categorías</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {formatCatalogCategory(category)}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-field">
          <label htmlFor="technology-filter">Tecnología</label>
          <select
            id="technology-filter"
            value={filters.technology}
            onChange={(event) => updateFilter("technology", event.target.value)}
            aria-describedby="catalog-filter-help catalog-result-count"
          >
            <option value="">Todas las tecnologías</option>
            {technologies.map((technology) => (
              <option key={technology} value={technology}>
                {technology}
              </option>
            ))}
          </select>
        </div>
        <button className="reset-button" type="button" onClick={() => setFilters(initialCatalogFilters)} disabled={!hasActiveFilters}>
          Restablecer criterios
        </button>
      </form>

      <p id="catalog-result-count" className="result-count" role="status" aria-live="polite" aria-atomic="true">
        {isUpdatingResults
          ? "Actualizando resultados…"
          : visibleProjects.length === 1
            ? "1 proyecto encontrado"
            : `${visibleProjects.length} proyectos encontrados`}
      </p>

      {visibleProjects.length > 0 ? (
        <div
          className="project-grid"
          role="region"
          aria-label="Resultados del catálogo"
          aria-live="polite"
          aria-atomic="false"
          aria-busy={isUpdatingResults}
        >
          {visibleProjects.map((project) => (
            <CatalogCard key={project.id} project={project} />
          ))}
        </div>
      ) : (
        <section className="catalog-state catalog-state--empty" role="status" aria-live="polite" aria-labelledby="no-results-title">
          <span className="state-icon" aria-hidden="true">
            0
          </span>
          <p className="eyebrow">Sin coincidencias</p>
          <h3 id="no-results-title">No encontramos proyectos con esos criterios</h3>
          <p>Prueba con otra búsqueda o restablece los filtros para volver a ver la colección completa.</p>
          <button className="text-button" type="button" onClick={() => setFilters(initialCatalogFilters)}>
            Ver todos los proyectos
          </button>
        </section>
      )}
    </section>
  );
}