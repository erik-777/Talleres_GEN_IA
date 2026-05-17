# Proyecto Final

## Proyecto Final: Implementación de un Agente de IA para Automatización de Tareas

Este proyecto final es el culmen de lo aprendido en los talleres anteriores. Los estudiantes deberán extender la arquitectura RAG para incluir un Agente de IA capaz de realizar acciones de forma autónoma, y luego desplegar esta solución en una interfaz web simple.

## Caso de Estudio

El objetivo sigue siendo el mismo: transformar el asistente de atención al cliente de EcoMarket en una herramienta proactiva. La tarea específica a automatizar es el proceso de devolución de productos, que ahora incluirá la verificación de elegibilidad y la generación de la etiqueta.

## Fase 1: Diseño de la Arquitectura del Agente

En esta fase, los estudiantes planificarán la arquitectura del agente y las herramientas que necesitará. La clave es la conceptualización y la justificación.

- **Extensión de la arquitectura RAG:** Dada la nueva modificación a través de un agente, la actual arquitectura RAG puede incorporarse ya sea como una nueva herramienta o como una ruta alterna al agente mismo, que puede definirse por reglas de entrada, como una arquitectura router.

- **Definición de las Herramientas (Tools):** Identificarán las "herramientas" que el agente usará para interactuar con sistemas externos. Por ejemplo, funciones como `verificar_elegibilidad_producto` y `generar_etiqueta_devolucion`. Se documentarán cómo estas herramientas —funciones simuladas— recibirán la información y qué tipo de respuesta devolverán. Deben utilizar un mínimo de dos (2) herramientas sin considerar la actual funcionalidad RAG.

- **Selección del Marco de Agentes:** Elegirán entre LangChain o LlamaIndex y justificarán por qué el marco seleccionado es el más apropiado para su flujo de trabajo, considerando la facilidad de uso y la capacidad de integrar las herramientas.

- **Planificación del Flujo de Trabajo:** Diseñarán un diagrama de flujo simple del proceso de devolución, detallando las decisiones del agente y las llamadas a las herramientas.

## Fase 2: Implementación y Conexión de Componentes

Esta es la fase de codificación. Los estudiantes deberán integrar su trabajo del Taller 2 con la nueva funcionalidad de agente.

- **Extensión del Código Base:** Deberán partir del código entregado en el anterior taller para agregar la lógica del agente. Esto implica definir las herramientas como funciones y luego inicializar el agente.

- **Manejo de Respuestas:** El agente no solo debe ejecutar la acción, sino también formatear la respuesta de vuelta al usuario de manera clara y amigable, manejando tanto el éxito como los posibles errores del proceso.

- **Evaluación del Comportamiento:** Se probará el agente con diferentes prompts para verificar que es capaz de discernir cuándo debe usar las herramientas y cuándo debe responder directamente.

## Fase 3: Análisis Crítico y Propuestas de Mejora

En esta fase, los estudiantes deberán reflexionar críticamente sobre las implicaciones de su trabajo.

- **Análisis de Seguridad y Ética:** Analizarán los nuevos riesgos éticos que surgen al darle a la IA la capacidad de tomar acciones. Pensarán en escenarios de riesgo y en cómo mitigarlos.

- **Monitoreo y Observabilidad:** Propondrán un sistema para asegurar que el agente funcione correctamente, como un registro de acciones o un sistema de alertas.

- **Propuestas de Mejora:** Pensarán en otras funcionalidades que podrían agregarse con agentes, como un agente que pueda crear una orden de reemplazo o actualizar la información del cliente en el CRM.

## Fase 4: Despliegue de la Aplicación

Esta es la fase final y de mayor impacto. Los estudiantes deberán empaquetar su solución y hacerla accesible a través de una interfaz de usuario.

- **Selección de la Herramienta:** Deberán elegir entre Streamlit o Gradio para construir la interfaz. Justificarán su elección basándose en la facilidad de uso y la funcionalidad.

- **Implementación de la Interfaz:** Crearán una aplicación simple con un campo de texto para el prompt del usuario y un área de visualización para la respuesta del agente. La interfaz debe ser intuitiva.

- **Demostración Funcional:** Los estudiantes deberán demostrar que su aplicación funciona de extremo a extremo, desde la entrada del usuario hasta la respuesta del agente.

## Forma de entrega

- Link del repositorio de GitHub que contiene la respuesta a las cuatro fases, de la misma manera en que se ha entregado para los talleres anteriores, respecto a la parte textual crítica y a la parte de código.

- Sustentación final de **15 minutos**, en donde se sustente la entrega del proyecto y se prueben los resultados de los distintos prompts y la respuesta del modelo, por medio del agente, a las peticiones. Esto hace parte de la demostración funcional necesaria de la fase 4.

# Rúbrica de Evaluación del Proyecto Final

**Puntaje total: 5 puntos**

## 1. Diseño de Arquitectura y Herramientas

**Valor: 1 punto**

- **1 punto:** El estudiante define claramente las herramientas del agente, selecciona un marco de trabajo apropiado y justifica su elección. El diseño del flujo de trabajo es lógico y bien planificado.

- **0 puntos:** El estudiante no define las herramientas de manera clara, o el diseño del flujo de trabajo es incompleto o incorrecto.

## 2. Implementación de Agentes y Conexión de Componentes

**Valor: 2 puntos**  
**Modalidad:** Sustentación

- **2 puntos:** El estudiante integra de manera exitosa el agente en el código base, demostrando una comprensión de cómo las piezas se conectan. El agente es capaz de tomar decisiones, usar las herramientas apropiadas y manejar tanto el éxito como el fallo de forma robusta.

- **1 punto:** El estudiante logra una implementación parcial. El agente puede usar las herramientas, pero el manejo de errores o la lógica de toma de decisiones es deficiente.

- **0 puntos:** El estudiante no logra implementar la funcionalidad del agente o la integración es incorrecta.

## 3. Análisis Crítico y Propuestas de Mejora

**Valor: 1 punto**

- **1 punto:** El estudiante presenta un análisis crítico y reflexivo sobre los riesgos éticos y de seguridad de su solución. Propone ideas de mejora y de monitoreo pertinentes.

- **0 puntos:** El estudiante presenta un análisis superficial o no aborda los riesgos críticos del uso de agentes en un entorno de producción.

## 4. Despliegue Funcional

**Valor: 1 punto**  
**Modalidad:** Sustentación

- **1 punto:** El estudiante despliega la solución en una interfaz funcional utilizando Streamlit o Gradio. La aplicación es intuitiva y permite a un usuario final interactuar de forma exitosa con el agente.

- **0 puntos:** El estudiante no logra desplegar la aplicación o la interfaz es defectuosa y no permite la interacción.
