import { describe, expect, it } from "vitest";

import { createManualMeasurement, loadDashboard } from "../src/lib/dashboard-client";
import { DashboardContractError, parseDashboard } from "../src/lib/dashboard-validation";

const validDashboard = {
  metadata: {
    contractVersion: "v1",
    source: "synthetic-fixture",
    generatedAt: "2026-09-01T09:00:00Z",
    notice: "Datos de prueba sintéticos.",
  },
  profile: { id: "sample-profile", displayName: "Perfil de prueba" },
  metrics: [{ id: "daily-steps", label: "Pasos", unit: "steps", category: "activity" }],
  measurements: [],
};

describe("cliente del dashboard", () => {
  it("usa la API cuando devuelve un dashboard válido y vacío", async () => {
    const fetcher = async () => new Response(JSON.stringify(validDashboard), { status: 200 });

    await expect(loadDashboard(fetcher)).resolves.toMatchObject({
      source: "api",
      warning: null,
      dashboard: { measurements: [] },
    });
  });

  it("usa el fixture local cuando la red falla", async () => {
    const fetcher = async () => Promise.reject(new Error("network unavailable"));

    await expect(loadDashboard(fetcher)).resolves.toMatchObject({
      source: "fixture",
      warning: expect.stringContaining("No se pudo conectar"),
    });
  });

  it("usa el fixture local cuando la API devuelve un error", async () => {
    const fetcher = async () => new Response(null, { status: 503 });

    await expect(loadDashboard(fetcher)).resolves.toMatchObject({
      source: "fixture",
      warning: expect.stringContaining("No se pudo conectar"),
    });
  });

  it("usa el fixture local cuando la respuesta incumple el contrato", async () => {
    const fetcher = async () => new Response(JSON.stringify({ metadata: {} }), { status: 200 });

    await expect(loadDashboard(fetcher)).resolves.toMatchObject({
      source: "fixture",
      warning: expect.stringContaining("no cumple el contrato"),
    });
  });

  it("envía una medición manual válida al endpoint v1", async () => {
    const fetcher = async (input: RequestInfo | URL, init?: RequestInit) => {
      expect(String(input)).toContain("/api/v1/measurements");
      expect(init?.method).toBe("POST");
      expect(init?.body).toBe(JSON.stringify({ metricId: "daily-steps", value: 900, recordedAt: "2026-09-02T08:00:00Z" }));
      return new Response(JSON.stringify({
        id: "manual-measurement-4",
        metricId: "daily-steps",
        value: 900,
        recordedAt: "2026-09-02T08:00:00Z",
        source: "manual",
      }), { status: 201 });
    };

    await expect(createManualMeasurement({ metricId: "daily-steps", value: 900, recordedAt: "2026-09-02T08:00:00Z" }, fetcher)).resolves.toMatchObject({
      measurement: { id: "manual-measurement-4", source: "manual" },
    });
  });

  it("rechaza una respuesta manual que no cumple el contrato", async () => {
    const fetcher = async () => new Response(JSON.stringify({ id: "invalid" }), { status: 201 });

    await expect(createManualMeasurement({ metricId: "daily-steps", value: 900, recordedAt: "2026-09-02T08:00:00Z" }, fetcher)).rejects.toThrow(DashboardContractError);
  });

  it("rechaza referencias de mediciones a métricas inexistentes", () => {
    expect(() => parseDashboard({ ...validDashboard, measurements: [{
      id: "orphan-measurement",
      metricId: "not-defined",
      value: 1,
      recordedAt: "2026-09-01T09:00:00Z",
      source: "synthetic",
    }] })).toThrow(DashboardContractError);
  });
});
