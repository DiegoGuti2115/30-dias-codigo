import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const stylesheet = readFileSync(resolve(process.cwd(), "src/app/globals.css"), "utf8");
const pageSource = readFileSync(resolve(process.cwd(), "src/app/page.tsx"), "utf8");
const dashboardSource = readFileSync(resolve(process.cwd(), "src/components/dashboard-view.tsx"), "utf8");

describe("regresiones de accesibilidad del recorrido principal", () => {
  it("mantiene enlace de salto, regiones semánticas y aviso no clínico", () => {
    expect(pageSource).toContain('href="#dashboard-content"');
    expect(pageSource).toContain('id="dashboard-content"');
    expect(pageSource).toContain('aria-label="Navegación principal"');
    expect(pageSource).toContain("no diagnostica");
  });

  it("expone estados, formularios etiquetados y alternativa tabular", () => {
    expect(dashboardSource).toContain('aria-busy="true"');
    expect(dashboardSource).toContain('role="alert"');
    expect(dashboardSource).toContain('htmlFor="metric-filter"');
    expect(dashboardSource).toContain("<caption>Tabla equivalente a la serie temporal");
    expect(dashboardSource).toContain('aria-describedby="trend-description"');
  });

  it("conserva foco visible y controles táctiles sin depender de hover", () => {
    expect(stylesheet).toContain(":focus-visible");
    expect(stylesheet).toContain(".skip-link:focus");
    expect(stylesheet).toContain("min-height: 2.6rem");
  });
});
