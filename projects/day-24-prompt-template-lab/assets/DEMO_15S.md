# 🎬 Guion de Demostración: Prompt Template Lab (15 Segundos)

Este archivo define la secuencia de grabación (GIF/MP4) para demostrar el funcionamiento de la Máquina de Estados (FSM) y la tolerancia a fallos del frontend en un entorno *Offline AI*.

## ⏱️ Secuencia de Grabación (Storyboard)

1. **[00:00 - 00:04] La Dinámica de Zod:**
   - **Acción:** Empieza con el editor de la izquierda. Escribe rápidamente: `"Traduce el texto {{documento}} al idioma {{idioma}}"`.
   - **Foco Visual:** Muestra cómo en el panel derecho (sección superior) aparecen instantáneamente los dos *inputs* generados dinámicamente.

2. **[00:04 - 00:07] Validación Estricta (Guardrail):**
   - **Acción:** Deja el campo `idioma` vacío y pulsa el botón "Compilar e Inferir".
   - **Foco Visual:** Haz zoom en el mensaje de error rojo del contrato de datos (`Falta la variable requerida: 'idioma'`), demostrando que el sistema intercepta fallos antes de llamar al LLM.

3. **[00:07 - 00:11] Ejecución en Entorno Mock:**
   - **Acción:** Rellena los campos con "Hola mundo" y "Francés". Asegúrate de que el *toggle* superior está en "Entorno Mock". Pulsa ejecutar.
   - **Foco Visual:** La consola terminal inferior muestra la respuesta estática instantáneamente, demostrando el desarrollo local sin dependencias.

4. **[00:11 - 00:15] Circuit Breaker en Acción (LLM API):**
   - **Acción:** Cambia el *toggle* a "API Local" (Ollama). Pulsa ejecutar nuevamente (mantén el demonio de Ollama apagado a propósito para forzar el fallo).
   - **Foco Visual:** Tras un breve estado de carga, la consola muestra la alerta `Fallback Activado` y renderiza la respuesta de seguridad del JSON.

---

## 📝 Copy para Publicación (Reto 30 Días - Proyecto 24)

**Día 24/30: Laboratorio de Plantillas de Prompt (Local-First & Resiliente) 🧪**

Construir interfaces para LLMs implica lidiar con dos grandes enemigos: la inestabilidad de las variables de contexto y las caídas de red de las APIs. Hoy he implementado un entorno de pruebas de Prompts diseñado para no colapsar nunca.

**🛠️ Decisiones Técnicas:**
- **Validación FSM en tiempo real:** Uso expresiones regulares y `Zod` para generar esquemas de validación dinámicos al vuelo. Si borras un `{{token}}` del prompt, el contrato muta; si envías datos vacíos, el sistema bloquea la inferencia. 
- **Offline AI & Circuit Breaker:** La suscripción a servicios cloud puede caducar (me pasó con Azure), así que reescribí el orquestador hacia Ollama (`phi3`). Implementé un *Circuit Breaker* (timeout de 3s): si el LLM local está apagado, el sistema conmuta instantáneamente a un Mock estático. Cero bloqueos en la UI.
- **UI/UX Enterprise:** Arquitectura *glassmórfica* oscura con separación semántica clara entre zona de configuración y consola de salida.

Código y documentación técnica 👇
[Enlace a GitHub]

#IngenieriaDeSoftware #React #TypeScript #InteligenciaArtificial #MachineLearning #MLOps