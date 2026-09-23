# Borrador para LinkedIn

🚀 **Día 23/30: Asistente de IA Conversacional con Streaming Nativo** 🤖

Para el proyecto de hoy en mi reto de 30 días de desarrollo, he construido un cliente de chat para Modelos de Lenguaje (LLMs) desde cero. Quería alejarme de las típicas UIs recargadas y apostar por un diseño verdaderamente minimalista, integrando funcionalidades de producción.

✨ **Highlights del proyecto:**
*   **Streaming en tiempo real:** Implementación nativa de Server-Sent Events (SSE) para renderizar la respuesta token a token, gestionando la fragmentación de chunks mediante un buffer en memoria.
*   **Arquitectura Resiliente:** Sistema de fallback automático. Si la cuota de la API se agota o la red falla, el sistema activa un "Modo Demo" (Mock) determinista para que la UI nunca se rompa.
*   **Persistencia Asíncrona:** Historial de sesión guardado localmente usando `IndexedDB` (no bloqueante) para no perder el contexto al recargar.
*   **UI/UX Minimalista:** Diseño limpio y sin distracciones utilizando Tailwind CSS, alejándome del concepto tradicional de "burbujas" para mejorar la legibilidad.

🛠️ **Stack Técnico:** React 18, TypeScript, Tailwind CSS, IndexedDB, Fetch API (ReadableStream).

El reto de hoy me ha servido para profundizar en el manejo de streams binarios en el navegador y cómo construir interfaces tolerantes a fallos cuando dependemos de APIs externas.

🔗 [Enlace al código en GitHub]

#React #TypeScript #WebDevelopment #ArtificialIntelligence #Frontend #30Dias30Proyectos #SoftwareEngineering