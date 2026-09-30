import type { CatalogProject } from "@/types/catalog";

type CatalogCardProperties = Readonly<{
  project: CatalogProject;
}>;

export function CatalogCard({ project }: CatalogCardProperties) {
  return (
    <article className="project-card">
      <div className="project-card__meta">
        <span>Día {String(project.day).padStart(2, "0")}</span>
        <span>{project.category}</span>
      </div>
      <h3>{project.name}</h3>
      <p>{project.summary}</p>
      <ul className="technology-list" aria-label={`Tecnologías de ${project.name}`}>
        {project.technologies.map((technology) => (
          <li key={technology}>{technology}</li>
        ))}
      </ul>
      <nav className="project-card__links" aria-label={`Recursos de ${project.name}`}>
        {project.links.map((link) => (
          <a key={link.href} href={link.href}>
            {link.label}
          </a>
        ))}
      </nav>
    </article>
  );
}