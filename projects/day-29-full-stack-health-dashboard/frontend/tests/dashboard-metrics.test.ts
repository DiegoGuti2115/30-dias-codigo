import { describe, expect, it } from "vitest";

import {
  buildMetricSeries,
  filterMeasurementsByRange,
  formatMeasurementValue,
  summarizeMetric,
} from "../src/lib/dashboard-metrics";
import type { HealthDashboardFixture, Measurement } from "../src/lib/dashboard-contract";

const measurements: Measurement[] = [
  { id: "metric-one", metricId: "daily-steps", value: 1200, recordedAt: "2026-09-01T09:00:00Z", source: "synthetic" },
  { id: "metric-two", metricId: "daily-steps", value: 1800, recordedAt: "2026-09-09T09:00:00Z", source: "manual" },
  { id: "metric-three", metricId: "water-intake", value: 700, recordedAt: "2026-09-08T09:00:00Z", source: "synthetic" },
];

const dashboard: HealthDashboardFixture = {
  metadata: { contractVersion: "v1", source: "synthetic-fixture", generatedAt: "2026-09-09T09:00:00Z", notice: "Demo" },
  profile: { id: "sample-profile", displayName: "Demo" },
  metrics: [
    { id: "daily-steps", label: "Pasos", unit: "steps", category: "activity" },
    { id: "water-intake", label: "Agua", unit: "ml", category: "hydration" },
  ],
  measurements,
};

describe("transformaciones de métricas", () => {
  it("filtra un periodo sin mutar ni desordenar la colección de entrada", () => {
    const result = filterMeasurementsByRange(measurements, "7d", new Date("2026-09-09T12:00:00Z"));

    expect(result.map((item) => item.id)).toEqual(["metric-three", "metric-two"]);
    expect(measurements.map((item) => item.id)).toEqual(["metric-one", "metric-two", "metric-three"]);
  });

  it("crea series vacías para métricas sin registros en el rango", () => {
    const series = buildMetricSeries(dashboard, "7d", new Date("2026-09-09T12:00:00Z"));

    expect(series).toHaveLength(2);
    expect(series[0].measurements).toHaveLength(1);
    expect(series[1].measurements).toHaveLength(1);
  });

  it("resume el último valor y soporta series vacías sin interpretar los valores", () => {
    const [steps] = buildMetricSeries(dashboard, "all", new Date("2026-09-09T12:00:00Z"));

    expect(summarizeMetric(steps)).toMatchObject({ total: 2, latest: { value: 1800 }, previous: { value: 1200 } });
    expect(summarizeMetric({ metric: steps.metric, measurements: [] })).toMatchObject({ total: 0, latest: null, previous: null });
  });

  it("formatea valores con unidad sin aplicar umbrales o etiquetas clínicas", () => {
    expect(formatMeasurementValue(7.5, "hours")).toBe("7,5 hours");
  });
});
