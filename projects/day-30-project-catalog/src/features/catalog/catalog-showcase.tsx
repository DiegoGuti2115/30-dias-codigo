import { CatalogCard } from "@/features/catalog/catalog-card";
import type { CatalogProject } from "@/types/catalog";

type CatalogShowcaseProperties = Readonly<{
  projects: readonly CatalogProject[];
}>;

export function CatalogShowcase({ projects }: CatalogShowcaseProperties) {
  return (
    <section className="catalog-showcase" aria-labelledby="featured-projects-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Vista de colección</p>
          <h2 id="featured-projects-title">Un sistema preparado para descubrir proyectos</h2>
        </div>
        <p>La búsqueda, los filtros y los enlaces se conectarán sobre esta jerarquía en la siguiente fase.</p>
      </div>
      <div className="project-grid">
        {projects.map((project) => (
          <CatalogCard key={project.id} project={project} />
        ))}
      </div>
    </section>
  );
}