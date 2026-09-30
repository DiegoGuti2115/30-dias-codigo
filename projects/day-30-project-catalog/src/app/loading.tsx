import { CatalogShell } from "@/components/catalog-shell";
import { CatalogCardSkeleton } from "@/features/catalog/catalog-card-skeleton";

export default function Loading() {
  return (
    <CatalogShell>
      <main id="catalog-content" className="catalog-main" aria-busy="true" aria-labelledby="loading-catalog-title">
        <section className="catalog-loading">
          <p className="eyebrow">Preparando colección</p>
          <h1 id="loading-catalog-title">Cargando el catálogo de proyectos</h1>
          <p role="status">Estamos preparando los proyectos para que puedas explorarlos.</p>
          <div className="skeleton-preview" aria-hidden="true">
            <CatalogCardSkeleton />
            <CatalogCardSkeleton />
            <CatalogCardSkeleton />
          </div>
        </section>
      </main>
    </CatalogShell>
  );
}