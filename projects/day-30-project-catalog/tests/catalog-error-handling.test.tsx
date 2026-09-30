import React from "react";
import Link from "next/link";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import GlobalError from "@/app/error";
import { CatalogState } from "@/components/catalog-state";

describe("catalog error handling", () => {
  it("renders a labelled recovery action in the source-error state", () => {
    render(
      <CatalogState
        kind="error"
        recovery={
          <Link className="text-button" href="/">
            Volver a intentar
          </Link>
        }
      />,
    );

    expect(screen.getByRole("region", { name: "No se pudo preparar el catálogo" })).toBeTruthy();
    expect(screen.getByRole("link", { name: "Volver a intentar" }).getAttribute("href")).toBe("/");
  });

  it("offers a retry action from the runtime error boundary", () => {
    const reset = vi.fn();
    const error = new Error("Rendering failed");
    vi.spyOn(console, "error").mockImplementation(() => undefined);

    render(<GlobalError error={error} reset={reset} />);
    fireEvent.click(screen.getByRole("button", { name: "Reintentar carga" }));

    expect(screen.getByRole("heading", { level: 1, name: "No pudimos mostrar el catálogo" })).toBeTruthy();
    expect(reset).toHaveBeenCalledOnce();
  });
});