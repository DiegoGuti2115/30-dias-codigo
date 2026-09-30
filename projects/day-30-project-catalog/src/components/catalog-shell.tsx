import type { ReactNode } from "react";

type CatalogShellProperties = Readonly<{
  children: ReactNode;
}>;

export function CatalogShell({ children }: CatalogShellProperties) {
  return (
    <div className="site-shell">
      <a className="skip-link" href="#catalog-content">
        Saltar al contenido principal
      </a>
      <header className="site-header">
        <a className="brand" href="#catalog-content" aria-label="Catálogo de proyectos, inicio">
          <span aria-hidden="true" className="brand-mark">
            30
          </span>
          <span className="brand-copy">
            <strong>Project Archive</strong>
            <span>30 Días, 30 Proyectos</span>
          </span>
        </a>
        <span className="header-status">Catálogo en construcción</span>
      </header>
      {children}
      <footer className="site-footer">
        <p>Proyecto de cierre de la mini-serie 30 Días, 30 Proyectos.</p>
        <a href="../../README.md">Ver el registro completo</a>
      </footer>
    </div>
  );
}