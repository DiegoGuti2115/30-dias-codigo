import type { ReactNode } from "react";

type CatalogStateKind = "loading" | "empty" | "error";

type CatalogStateProperties = Readonly<{
  kind: CatalogStateKind;
  recovery?: ReactNode;
}>;

const stateContent: Record<CatalogStateKind, Readonly<{ eyebrow: string; title: string; description: string }>> = {
  loading: {
    eyebrow: "Preparando colección",
    title: "Cargando los proyectos del reto",
    description: "La estructura visual reserva espacio para una carga clara y sin cambios bruscos de contenido.",
  },
  empty: {
    eyebrow: "Colección vacía",
    title: "Aún no hay proyectos para mostrar",
    description: "Cuando la fuente local no tenga entradas, este estado explicará la situación sin dejar una pantalla vacía.",
  },
  error: {
    eyebrow: "Datos no disponibles",
    title: "No se pudo preparar el catálogo",
    description: "El diseño ofrece un lugar consistente para comunicar un error recuperable de la fuente de datos.",
  },
};

export function CatalogState({ kind, recovery }: CatalogStateProperties) {
  const content = stateContent[kind];

  return (
    <section className={`catalog-state catalog-state--${kind}`} aria-labelledby={`${kind}-state-title`}>
      <span className="state-icon" aria-hidden="true">
        {kind === "error" ? "!" : "· · ·"}
      </span>
      <p className="eyebrow">{content.eyebrow}</p>
      <h2 id={`${kind}-state-title`}>{content.title}</h2>
      <p>{content.description}</p>
      {recovery}
    </section>
  );
}