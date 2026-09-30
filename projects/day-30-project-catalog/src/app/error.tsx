"use client";

import { useEffect } from "react";

type GlobalErrorProperties = Readonly<{
  error: Error & { digest?: string };
  reset: () => void;
}>;

export default function GlobalError({ error, reset }: GlobalErrorProperties) {
  useEffect(() => {
    console.error("Catalog rendering error", error);
  }, [error]);

  return (
    <main className="catalog-main error-page" aria-labelledby="runtime-error-title">
      <section className="catalog-state catalog-state--error">
        <span className="state-icon" aria-hidden="true">
          !
        </span>
        <p className="eyebrow">Error recuperable</p>
        <h1 id="runtime-error-title">No pudimos mostrar el catálogo</h1>
        <p>La información no se ha podido preparar en este momento. Puedes volver a intentarlo sin perder el acceso a la página.</p>
        <button className="text-button" type="button" onClick={reset}>
          Reintentar carga
        </button>
      </section>
    </main>
  );
}