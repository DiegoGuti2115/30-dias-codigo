import { describe, expect, it } from "vitest";

import { DASHBOARD_CONTRACT_VERSION } from "../src/lib/dashboard-contract";

describe("adaptador de contrato compartido", () => {
  it("expone la versión v1 para los consumidores de frontend", () => {
    expect(DASHBOARD_CONTRACT_VERSION).toBe("v1");
  });
});
