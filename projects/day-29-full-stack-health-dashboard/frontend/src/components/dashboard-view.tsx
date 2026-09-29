"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  createManualMeasurement,
  loadDashboard,
  type DashboardLoadResult,
} from "../lib/dashboard-client";
import {
  buildMetricSeries,
  formatMeasurementValue,
  summarizeMetric,
  type TimeRange,
} from "../lib/dashboard-metrics";

interface DashboardState {
  status: "loading" | "ready";
  result: DashboardLoadResult | null;
}

interface SubmissionState {
  message: string | null;
  status: "idle" | "submitting" | "success" | "error";
}

const initialState: DashboardState = { status: "loading", result: null };
const initialSubmission: SubmissionState = { status: "idle", message: null };

function statusLabel(source: DashboardLoadResult["source"]): string {
  return source === "api" ? "API local disponible" : "Fixture local de demostración";
}

function rangeLabel(range: TimeRange): string {
  return range === "7d" ? "Últimos 7 días" : range === "30d" ? "Últimos 30 días" : "Todo el historial";
}

function dateInputValue(): string {
  return new Date().toISOString().slice(0, 16);
}

export function DashboardView() {
  const [state, setState] = useState<DashboardState>(initialState);
  const [range, setRange] = useState<TimeRange>("all");
  const [selectedMetricId, setSelectedMetricId] = useState<string>("");
  const [submission, setSubmission] = useState<SubmissionState>(initialSubmission);

  useEffect(() => {
    let active = true;
    void loadDashboard().then((result) => {
      if (active) {
        setState({ status: "ready", result });
        setSelectedMetricId(result.dashboard.metrics[0]?.id ?? "");
      }
    });
    return () => { active = false; };
  }, []);

  const series = useMemo(() => {
    if (!state.result) return [];
    return buildMetricSeries(state.result.dashboard, range, new Date());
  }, [range, state.result]);

  async function submitMeasurement(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!state.result || !selectedMetricId) return;

    const form = new FormData(event.currentTarget);
    const value = Number(form.get("value"));
    const recordedAt = String(form.get("recordedAt"));
    if (!Number.isFinite(value) || !recordedAt) {
      setSubmission({ status: "error", message: "Introduce un valor numérico finito y una fecha válida." });
      return;
    }

    setSubmission({ status: "submitting", message: null });
    try {
      const { measurement } = await createManualMeasurement({
        metricId: selectedMetricId,
        value,
        recordedAt: new Date(recordedAt).toISOString(),
      });
      setState((current) => current.result ? {
        status: "ready",
        result: { ...current.result, dashboard: { ...current.result.dashboard, measurements: [...current.result.dashboard.measurements, measurement] } },
      } : current);
      event.currentTarget.reset();
      setSubmission({ status: "success", message: "La medición manual se añadió a esta sesión local." });
    } catch {
      setSubmission({ status: "error", message: "No se pudo guardar la medición. Comprueba que la API local esté disponible." });
    }
  }

  if (state.status === "loading" || !state.result) {
    return <section aria-busy="true" aria-live="polite" className="data-state" role="status"><h2>Cargando datos de demostración</h2><p>Se está consultando la fuente local configurada.</p></section>;
  }

  const { dashboard, source, warning } = state.result;
  const selectedSeries = series.find((item) => item.metric.id === selectedMetricId) ?? series[0];
  const selectedMetric = selectedSeries?.metric;
  const visibleMeasurements = selectedSeries?.measurements ?? [];

  return (
    <section aria-live="polite" className="dashboard-content">
      <div className="source-status" role="status"><strong>Origen de datos: {statusLabel(source)}</strong><span>{dashboard.metadata.notice}</span></div>
      {warning ? <div className="source-warning" role="alert"><strong>Fuente alternativa activa.</strong> {warning}</div> : null}

      <section aria-labelledby="profile-heading" className="profile-card">
        <p className="eyebrow">Perfil de demostración</p><h2 id="profile-heading">{dashboard.profile.displayName}</h2>
        <p>Contrato {dashboard.metadata.contractVersion} · generado el {new Intl.DateTimeFormat("es-ES", { dateStyle: "medium", timeStyle: "short" }).format(new Date(dashboard.metadata.generatedAt))}</p>
      </section>

      <section aria-labelledby="summary-heading">
        <div className="section-heading"><div><p className="eyebrow">Resumen no clínico</p><h2 id="summary-heading">Últimos registros por métrica</h2></div><span>{rangeLabel(range)}</span></div>
        <div className="range-controls" aria-label="Filtro temporal">
          {(["7d", "30d", "all"] as TimeRange[]).map((option) => <button className={range === option ? "is-selected" : ""} key={option} onClick={() => setRange(option)} type="button">{rangeLabel(option)}</button>)}
        </div>
        <div className="summary-grid">
          {series.map((item) => {
            const summary = summarizeMetric(item);
            return <article className="metric-summary" key={item.metric.id}><h3>{item.metric.label}</h3><p className="summary-value">{summary.latest ? formatMeasurementValue(summary.latest.value, item.metric.unit) : "Sin registros"}</p><p>{summary.total} registro{summary.total === 1 ? "" : "s"} en el periodo.</p></article>;
          })}
        </div>
      </section>

      <section aria-labelledby="trend-heading">
        <div className="section-heading"><div><p className="eyebrow">Serie temporal</p><h2 id="trend-heading">Tendencia de registros</h2></div></div>
        <label className="field-label" htmlFor="metric-filter">Métrica mostrada</label>
        <select id="metric-filter" onChange={(event) => setSelectedMetricId(event.target.value)} value={selectedMetricId}>
          {dashboard.metrics.map((metric) => <option key={metric.id} value={metric.id}>{metric.label}</option>)}
        </select>
        {selectedMetric ? <div className="trend-card">
          <p id="trend-description">Secuencia cronológica de valores registrados para {selectedMetric.label}; solo describe datos de demostración y no interpreta su significado.</p>
          {visibleMeasurements.length ? <ol aria-describedby="trend-description" className="trend-list">{visibleMeasurements.map((measurement) => <li key={measurement.id}><strong>{formatMeasurementValue(measurement.value, selectedMetric.unit)}</strong><span>{new Intl.DateTimeFormat("es-ES", { dateStyle: "medium", timeStyle: "short" }).format(new Date(measurement.recordedAt))} · {measurement.source === "manual" ? "Manual" : "Sintético"}</span></li>)}</ol> : <div className="data-state" role="status"><h3>Sin registros en este periodo</h3><p>Selecciona otro periodo o añade una medición de demostración.</p></div>}
        </div> : null}
      </section>

      <section aria-labelledby="entry-heading" className="entry-card">
        <div className="section-heading"><div><p className="eyebrow">Captura local</p><h2 id="entry-heading">Añadir medición manual</h2></div></div>
        <p>Los valores se guardan únicamente en memoria mientras la API local permanezca activa. No se aplican umbrales, objetivos ni interpretaciones.</p>
        <form className="measurement-form" onSubmit={submitMeasurement}>
          <label><span>Métrica</span><select onChange={(event) => setSelectedMetricId(event.target.value)} value={selectedMetricId}>{dashboard.metrics.map((metric) => <option key={metric.id} value={metric.id}>{metric.label} ({metric.unit})</option>)}</select></label>
          <label><span>Valor registrado</span><input inputMode="decimal" name="value" required step="any" type="number" /></label>
          <label><span>Fecha y hora</span><input defaultValue={dateInputValue()} name="recordedAt" required type="datetime-local" /></label>
          <button disabled={submission.status === "submitting"} type="submit">{submission.status === "submitting" ? "Guardando…" : "Guardar medición"}</button>
        </form>
        {submission.message ? <p className={submission.status === "error" ? "form-message error" : "form-message success"} role={submission.status === "error" ? "alert" : "status"}>{submission.message}</p> : null}
      </section>

      <section aria-labelledby="measurements-heading">
        <div className="section-heading"><div><p className="eyebrow">Alternativa tabular</p><h2 id="measurements-heading">Registros de {selectedMetric?.label ?? "métricas"}</h2></div><span>{visibleMeasurements.length} registros</span></div>
        {visibleMeasurements.length ? <div className="table-wrap"><table><caption>Tabla equivalente a la serie temporal, filtrada por métrica y periodo.</caption><thead><tr><th>Valor</th><th>Fecha</th><th>Origen</th></tr></thead><tbody>{visibleMeasurements.map((measurement) => <tr key={measurement.id}><td>{selectedMetric ? formatMeasurementValue(measurement.value, selectedMetric.unit) : measurement.value}</td><td>{new Intl.DateTimeFormat("es-ES", { dateStyle: "medium", timeStyle: "short" }).format(new Date(measurement.recordedAt))}</td><td>{measurement.source === "manual" ? "Manual" : "Sintético"}</td></tr>)}</tbody></table></div> : <div className="data-state" role="status"><h3>No hay mediciones disponibles</h3><p>La fuente se cargó correctamente, pero no contiene registros para el filtro actual.</p></div>}
      </section>
    </section>
  );
}
