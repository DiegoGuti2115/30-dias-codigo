import { DashboardView } from "../components/dashboard-view";

export default function HomePage() {
  return (
    <main className="app-shell">
      <a className="skip-link" href="#dashboard-content">Saltar al contenido principal</a>
      <header className="site-header">
        <div>
          <p className="eyebrow">Demo local · datos sintéticos</p>
          <h1>Dashboard de bienestar</h1>
        </div>
        <nav aria-label="Navegación principal">
          <a href="#datos">Datos</a>
          <a href="#limites">Límites de uso</a>
        </nav>
      </header>

      <section aria-labelledby="notice-heading" className="non-clinical-notice" id="limites">
        <h2 id="notice-heading">Uso informativo y no clínico</h2>
        <p>Esta demo no diagnostica, no interpreta valores y no ofrece recomendaciones médicas.</p>
      </section>

      <div id="dashboard-content" tabIndex={-1}>
        <DashboardView />
      </div>

      <footer className="site-footer" id="datos">
        <p>Los datos mostrados son sintéticos o de demostración local. No incluyas información personal ni sanitaria real.</p>
      </footer>
    </main>
  );
}
