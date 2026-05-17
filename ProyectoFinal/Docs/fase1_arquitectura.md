# Fase 1: Diseño de la Arquitectura del Agente

## 1. Extensión de la Arquitectura RAG

El sistema RAG del Taller 2 (ChromaDB + OpenAI Embeddings + GPT-3.5-turbo) se incorpora como una **herramienta más del agente** (`buscar_politicas_ecomarket`). Esto sigue el patrón de **arquitectura router implícita**: el LLM del agente decide en tiempo de ejecución si la consulta requiere una búsqueda vectorial semántica, una consulta a la base de datos de pedidos, o una acción transaccional (verificar/generar devolución).

Esta decisión se toma por el propio razonamiento del agente (ReAct / OpenAI Tools), sin reglas de ruteo escritas en código, lo cual es más flexible que un router basado en reglas fijas.

```
Usuario
  │
  ▼
create_react_agent (LangGraph + GPT-4o-mini)
  │
  ├──► consultar_estado_pedido        → JSON legacy_data/orders.json
  │
  ├──► verificar_elegibilidad_devolucion  → JSON orders.json + return_policies.json
  │
  ├──► generar_etiqueta_devolucion    → Lógica simulada (UUID + fecha)
  │
  └──► buscar_politicas_ecomarket     → ChromaDB (RAG Taller 2)
                                           └─► OpenAI text-embedding-3-small
                                           └─► knowledge_base/*.md
```

---

## 2. Definición de las Herramientas (Tools)

### Tool 1: `consultar_estado_pedido`
- **Entrada:** `numero_seguimiento: str` (ej: `"ECO1004"`)
- **Proceso:** Busca el pedido en `legacy_data/orders.json` por número de tracking (case-insensitive)
- **Salida:** Nombre del cliente, producto, estado, fecha de entrega estimada, enlace de tracking, y razón de retraso si aplica
- **Cuándo la usa el agente:** Cuando el cliente pregunta por el estado, ubicación o fecha de entrega de un pedido

### Tool 2: `verificar_elegibilidad_devolucion`
- **Entrada:** `numero_seguimiento: str`
- **Proceso:**
  1. Verifica que el pedido exista
  2. Verifica que el estado sea `"Entregado"` (condición necesaria)
  3. Mapea el nombre del producto a una categoría de política usando palabras clave
  4. Consulta `return_policies.json` para obtener la política de esa categoría
- **Salida:** Resultado de elegibilidad con condiciones específicas o razón de rechazo
- **Cuándo la usa el agente:** Siempre como primer paso ante cualquier solicitud de devolución, antes de generar la etiqueta

### Tool 3: `generar_etiqueta_devolucion`
- **Entrada:** `numero_seguimiento: str`, `motivo_devolucion: str`
- **Proceso:** Genera un código único de devolución (`RET-XXXXXXXX`), calcula fecha de vencimiento (15 días), y formatea instrucciones de envío
- **Salida:** Etiqueta completa con código, producto, cliente, motivo, fecha de vencimiento e instrucciones
- **Cuándo la usa el agente:** Solo después de confirmar elegibilidad con la Tool 2

### Tool 4: `buscar_politicas_ecomarket` (RAG integrado)
- **Entrada:** `consulta: str` (pregunta en lenguaje natural)
- **Proceso:** Genera embedding de la consulta con `text-embedding-3-small`, recupera los 3 chunks más similares de ChromaDB
- **Salida:** Fragmentos relevantes de la base de conocimiento (políticas, FAQs, categorías)
- **Cuándo la usa el agente:** Para preguntas generales sobre políticas, plazos, condiciones y FAQs

---

## 3. Selección del Marco de Agentes: LangChain

Se eligió **LangChain** sobre LlamaIndex por las siguientes razones:

| Criterio | LangChain | LlamaIndex |
|---|---|---|
| Continuidad con Taller 2 | ✅ Ya se usaba LangChain | ❌ Requeriría reescribir el RAG |
| Integración de tools con OpenAI | ✅ `create_react_agent` (LangGraph prebuilt) | ⚠️ Más verboso |
| Manejo de historial de chat | ✅ `MessagesPlaceholder` built-in | ✅ También disponible |
| Documentación y ecosistema | ✅ Muy amplio | ✅ Bueno pero más enfocado en RAG |
| Facilidad para definir tools | ✅ Decorador `@tool` | ⚠️ Requiere más boilerplate |

**Conclusión:** LangChain + LangGraph permite reutilizar directamente el código del Taller 2 y ofrece el decorador `@tool` que simplifica enormemente la definición de herramientas. `create_react_agent` de LangGraph proporciona un historial de mensajes estructurado que permite extraer los pasos intermedios (herramientas usadas, inputs y outputs) necesarios para la observabilidad en la interfaz Streamlit.

---

## 4. Diagrama de Flujo del Proceso de Devolución

```
[Cliente escribe consulta]
         │
         ▼
[AgentExecutor analiza intent]
         │
         ├─ ¿Pregunta de estado? ──────────────► consultar_estado_pedido
         │                                              │
         │                                              ▼
         │                                    [Devuelve estado al cliente]
         │
         ├─ ¿Solicitud de devolución? ─────► verificar_elegibilidad_devolucion
         │                                              │
         │                              ┌──────────────┴──────────────┐
         │                              ▼                             ▼
         │                        [NO ELEGIBLE]               [SÍ ELEGIBLE]
         │                              │                             │
         │                    [Explica motivo +              ¿Tiene motivo?
         │                    ofrece contacto]                        │
         │                                               ┌────────────┴────────────┐
         │                                               ▼                         ▼
         │                                        [Pide motivo]            generar_etiqueta_devolucion
         │                                                                          │
         │                                                                 [Entrega etiqueta + instrucciones]
         │
         └─ ¿Pregunta general? ───────────────► buscar_politicas_ecomarket
                                                          │
                                                 [Responde con contexto RAG]
```
