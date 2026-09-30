import Link from "next/link";

import { CatalogShell } from "@/components/catalog-shell";
import { CatalogState } from "@/components/catalog-state";
import { CatalogBrowser } from "@/features/catalog/catalog-browser";
import { loadLocalCatalog } from "@/lib/catalog-source";

export default function HomePage() {
  const catalogResult = loadLocalCatalog();

  if (!catalogResult.ok) {
    return (
      <CatalogShell>
        <main id="catalog-content" className="catalog-main">
          <CatalogHero projectCount={0} />
          <CatalogState
            kind="error"
            recovery={
              <Link className="text-button" href="/">
                Volver a intentar
              </Link>
            }
          />
        </main>
      </CatalogShell>
    );
  }

  return (
    <CatalogShell>
      <main id="catalog-content" className="catalog-main">
        <CatalogHero projectCount={catalogResult.catalog.projects.length} />
        <CatalogBrowser projects={catalogResult.catalog.projects} />
      </main>
    </CatalogShell>
  );
}

type CatalogHeroProperties = Readonly<{
  projectCount: number;
}>;

function CatalogHero({ projectCount }: CatalogHeroProperties) {
  return (
    <section className="catalog-hero" aria-labelledby="catalog-title">
      <div className="hero-copy">
        <p className="eyebrow">Día 30 · Proyecto de cierre</p>
        <h1 id="catalog-title">Una colección para recorrer todo lo construido.</h1>
        <p>
          El Catálogo de proyectos reúne treinta entregas de ingeniería en un sistema visual claro, adaptable y
          preparado para explorar sin fricción.
        </p>
      </div>
      <dl className="catalog-summary" aria-label="Resumen de la colección">
        <div>
          <dt>{projectCount}</dt>
          <dd>proyectos documentados</dd>
        </div>
        <div>
          <dt>6</dt>
          <dd>áreas de exploración</dd>
        </div>
        <div>
          <dt>01—30</dt>
          <dd>un recorrido completo</dd>
        </div>
      </dl>
    </section>
  );
}