# Proyecto Final — Respuestas y Documentación

## Estructura del Proyecto

```
ProyectoFinal/
├── agente_ecomarket.py      # Agente principal con 4 tools + RAG
├── app.py                   # Interfaz Streamlit (Fase 4)
├── styles.css               # Estilos de la interfaz (separados de app.py)
├── requirements.txt         # Dependencias
├── chroma_db/               # Base vectorial (persistida, reutilizada entre reinicios)
├── Docs/
│   ├── fase1_arquitectura.md    # Diseño, tools, justificación LangChain, diagrama
│   ├── fase3_analisis_critico.md # Ética, seguridad, monitoreo, mejoras
│   └── ProyectoFinal.pdf        # Rúbrica original
└── RESPUESTAS.md            # Este archivo
```

El proyecto extiende el código del Taller 2 (`../Taller2/`). Los datos de pedidos,
políticas y la base de conocimiento se leen directamente desde esa carpeta sin duplicación.

---

## Fase 1 — Diseño de Arquitectura

Ver: [`docs/fase1_arquitectura.md`](docs/fase1_arquitectura.md)

**Resumen:**
- **Marco elegido:** LangChain + LangGraph con `create_react_agent` (prebuilt)
- **Justificación:** Continuidad con Taller 2, decorador `@tool` simple, historial de mensajes nativo para observabilidad en UI
- **RAG integrado:** Como tool `buscar_politicas_ecomarket` (arquitectura router implícita)
- **Tools definidas (4):**

| Tool | Entrada | Acción |
|---|---|---|
| `consultar_estado_pedido` | `numero_seguimiento` | Lookup JSON orders |
| `verificar_elegibilidad_devolucion` | `numero_seguimiento` | Verifica estado + política de categoría |
| `generar_etiqueta_devolucion` | `numero_seguimiento`, `motivo` | Genera código RET-XXXXXXXX + instrucciones |
| `buscar_politicas_ecomarket` | `consulta` | Búsqueda semántica ChromaDB (RAG Taller 2) |

---

## Fase 2 — Implementación

Ver: [`agente_ecomarket.py`](agente_ecomarket.py)

**Cómo ejecutar en terminal:**
```bash
cd ProyectoFinal
python agente_ecomarket.py
```

**Decisiones de implementación:**
- Modelo: `gpt-4o-mini` (reemplaza `gpt-3.5-turbo`, retirado por OpenAI en enero 2025)
- `_extract_steps()` parsea el historial de mensajes LangGraph para capturar qué tools usó el agente en cada respuesta
- Singleton `_agent` y `_vector_db` para no reinicializar en cada llamada desde Streamlit
- `get_vector_db()` reutiliza la ChromaDB persistida si ya existe; solo regenera el índice en el primer arranque
- El `SYSTEM_PROMPT` y los docstrings de cada tool definen el flujo obligatorio para que el agente no falle ante casos no previstos

**Prompts de prueba para sustentación:**

| Prompt | Tools esperadas | Resultado esperado |
|---|---|---|
| `¿Estado del pedido ECO1004?` | `consultar_estado_pedido` | Estado: Retrasado, con motivo |
| `Quiero devolver ECO1002` | `verificar_elegibilidad_devolucion` | Elegible (Cepillo de bambú, entregado) |
| `Quiero devolver ECO1002, llegó roto` | `verificar_elegibilidad` → `generar_etiqueta` | Etiqueta con código RET-XXXXXXXX |
| `Quiero devolver ECO1001` | `verificar_elegibilidad_devolucion` | No elegible (estado: En tránsito) |
| `¿Puedo devolver un shampoo abierto?` | `buscar_politicas_ecomarket` | Respuesta de política de higiene |
| `¿Cuántos días tengo para devolver?` | `buscar_politicas_ecomarket` | 30 días calendario |

---

## Fase 3 — Análisis Crítico

Ver: [`docs/fase3_analisis_critico.md`](docs/fase3_analisis_critico.md)

**Riesgos principales identificados:**
1. Acciones no autorizadas (devoluciones fraudulentas) — mitigable con autenticación
2. Prompt injection — mitigable con sanitización y uso de Function Calling
3. Alucinación en decisiones transaccionales — mitigado con flujo obligatorio en system prompt
4. Discriminación percibida por política de categoría — mitigado con explicaciones transparentes
5. Privacidad de datos — requiere autenticación en producción

**Sistema de monitoreo propuesto:** LangSmith para trazabilidad completa + action log en BD + alertas por Slack.

---

## Fase 4 — Despliegue

Ver: [`app.py`](app.py)

**Herramienta elegida: Streamlit**

**Justificación sobre Gradio:**
- Streamlit ofrece control más granular sobre el layout (sidebar, columnas, expanders)
- El componente `st.chat_message` proporciona una UI de chat nativa y limpia
- `st.cache_resource` permite cachear el agente y el vector store entre sesiones sin reinicializar
- Gradio es más adecuado para demos de modelos individuales; Streamlit es mejor para aplicaciones con estado y múltiples componentes

**Cómo ejecutar:**
```bash
cd ProyectoFinal
streamlit run app.py
```

**Características de la interfaz:**
- Header con gradiente de marca EcoMarket y paleta CSS consistente (`styles.css` separado de `app.py`)
- Panel de métricas en tiempo real (4 indicadores actualizados tras cada respuesta):
  - Consultas realizadas en la sesión
  - Total de llamadas a tools
  - Tiempo de respuesta promedio
  - Tool más usada con contador
- Chat con historial de conversación persistente en sesión
- 4 botones de consultas sugeridas en la primera carga
- Timeline de herramientas: pasos numerados con ícono por tool, tiempo de respuesta por turno, y detalle de inputs/outputs expandible
- Sidebar con estado del agente (punto animado), guía de herramientas y pedidos de prueba
- Manejo de errores con mensaje amigable y referencia a soporte
