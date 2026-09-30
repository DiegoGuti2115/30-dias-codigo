import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Catálogo de proyectos | 30 Días, 30 Proyectos",
  description: "Explora los 30 proyectos de la mini-serie con búsqueda, filtros accesibles y recursos locales validados.",
  applicationName: "Catálogo de proyectos",
  robots: {
    index: true,
    follow: true,
  },
};

type RootLayoutProperties = Readonly<{
  children: React.ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProperties) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}