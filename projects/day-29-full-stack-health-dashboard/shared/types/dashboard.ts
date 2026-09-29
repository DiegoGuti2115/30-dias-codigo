/**
 * Tipos TypeScript sincronizados manualmente con
 * shared/contracts/v1/dashboard.schema.json.
 *
 * El contrato describe datos de bienestar no clínicos. No representa
 * diagnósticos, umbrales, alertas ni recomendaciones.
 */

export const DASHBOARD_CONTRACT_VERSION = "v1" as const;

export type MetricCategory = "activity" | "rest" | "hydration" | "wellbeing";
export type MeasurementSource = "manual" | "synthetic";

export interface FixtureMetadata {
  contractVersion: typeof DASHBOARD_CONTRACT_VERSION;
  source: "synthetic-fixture";
  generatedAt: string;
  notice: string;
}

export interface HealthProfile {
  id: string;
  displayName: string;
}

export interface MetricDefinition {
  id: string;
  label: string;
  unit: string;
  category: MetricCategory;
}

export interface Measurement {
  id: string;
  metricId: string;
  value: number;
  recordedAt: string;
  source: MeasurementSource;
}

export interface HealthDashboardFixture {
  metadata: FixtureMetadata;
  profile: HealthProfile;
  metrics: MetricDefinition[];
  measurements: Measurement[];
}
