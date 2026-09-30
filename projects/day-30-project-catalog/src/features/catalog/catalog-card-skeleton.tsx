export function CatalogCardSkeleton() {
  return (
    <article className="project-card project-card--skeleton" aria-label="Vista previa de tarjeta de proyecto">
      <div className="skeleton-line skeleton-line--short" />
      <div className="skeleton-line skeleton-line--title" />
      <div className="skeleton-line" />
      <div className="skeleton-line skeleton-line--medium" />
      <div className="skeleton-tags" aria-hidden="true">
        <span />
        <span />
      </div>
    </article>
  );
}