# Taller Práctico #2: Optimización de la Atención al Cliente - EcoMarket

## Fase 1: Selección de Componentes Clave del Sistema RAG

### 1. Modelo de Embeddings
**Selección:** `text-embedding-3-small` de OpenAI.

**Justificación:**
*   **Precisión:** Este modelo ofrece un rendimiento de vanguardia en la captura de matices semánticos, superando a muchos modelos de código abierto en tareas multilingües.
*   **Costo:** Es extremadamente económico ($0.02 por cada 1M de tokens), lo que lo hace ideal para una empresa de E-commerce como EcoMarket que maneja grandes volúmenes de consultas.
*   **Idioma Español:** Tiene un soporte nativo excelente para el español, capturando jerga y contextos locales que a menudo se pierden en modelos más básicos.
*   **Propiedad:** Aunque es propietario, la facilidad de integración y la infraestructura escalable de OpenAI compensan la falta de control directo sobre el modelo.

### 2. Base de Datos Vectorial
**Selección:** `ChromaDB`.

**Justificación:**
*   **Facilidad de Uso:** Es una base de datos de código abierto que se puede ejecutar localmente con una configuración mínima, lo que acelera el desarrollo y las pruebas del prototipo para EcoMarket.
*   **Costo:** Al ser self-hosted y de código abierto, el costo de infraestructura inicial es cero, a diferencia de Pinecone (que tiene capas gratuitas pero limitaciones de escalabilidad en sus tiers bajos).
*   **Escalabilidad:** Para las necesidades actuales de EcoMarket (documentación interna, FAQ, políticas), ChromaDB maneja perfectamente miles de vectores. Si la empresa crece masivamente, se puede migrar a soluciones en la nube, pero para este taller es la opción más eficiente.

---

## Fase 2: Creación de la Base de Conocimiento de Documentos

### 1. Identificación de Documentos
Para EcoMarket, hemos seleccionado los siguientes documentos críticos:
1.  **Política de Devoluciones y Garantías (PDF):** Documento detallado sobre plazos, condiciones de productos abiertos y procesos de reembolso.
2.  **Preguntas Frecuentes - FAQ (Markdown/JSON):** Compilación de las dudas más comunes de los usuarios sobre tiempos de envío, métodos de pago y cobertura.
3.  **Catálogo de Productos y Especificaciones (JSON/CSV):** Información técnica de los productos para responder dudas sobre compatibilidad o materiales.

### 2. Segmentación (Chunking)
**Estrategia:** `RecursiveCharacterTextSplitter` (Segmentación Recursiva).

**Justificación:**
Esta estrategia es superior para este caso de uso porque intenta mantener los párrafos y oraciones juntos. Divide el texto basándose en una jerarquía de caracteres (párrafos `\n\n`, líneas `\n`, espacios ` `).
*   **Preservación de Contexto:** Evita que una regla de devolución se corte a la mitad, asegurando que el modelo reciba la instrucción completa.
*   **Flexibilidad:** Se adapta a diferentes formatos de documentos (PDFs largos vs FAQs cortos).

### 3. Indexación
El proceso de indexación seguirá estos pasos:
1.  **Carga:** Los documentos se cargan usando `DirectoryLoader` de LangChain.
2.  **Transformación:** Se aplica el `RecursiveCharacterTextSplitter` con un `chunk_size` de 1000 y `chunk_overlap` de 200 (para no perder contexto entre fragmentos).
3.  **Conversión:** Cada fragmento se envía al modelo `text-embedding-3-small` para generar su representación vectorial.
4.  **Almacenamiento:** Los vectores resultantes, junto con su metadata (fuente, página), se guardan en una colección de `ChromaDB`.

---

## Fase 3: Limitaciones y Suposiciones

### Limitaciones
1.  **Dependencia de la Calidad del OCR:** Para documentos PDF, la precisión del sistema RAG depende de la calidad de la extracción de texto. Si el documento tiene tablas complejas o imágenes con texto, la recuperación puede ser deficiente.
2.  **Latencia:** Al utilizar modelos de OpenAI vía API, existe una latencia inherente de red. No es una solución de tiempo real puro, aunque es aceptable para un chat de soporte.
3.  **Costo de Tokens:** Aunque `text-embedding-3-small` es económico, un volumen masivo de documentos e indexaciones frecuentes podría generar costos significativos a largo plazo.

### Suposiciones
1.  **Conectividad Constante:** Se asume que el servidor donde corre el script tiene acceso estable a internet para comunicarse con la API de OpenAI.
2.  **Formato de Documentos:** Se asume que los documentos en la carpeta `knowledge_base` siguen una estructura lógica (títulos, párrafos claros) para facilitar el chunking recursivo.
---

## Fase 4: Integración con la Entrega Anterior (Taller #1)

Para esta entrega, se ha "ajustado" el modelo anterior integrando sus capacidades lógicas con el nuevo sistema RAG:

1.  **Migración de Datos:** Se han incorporado los archivos `orders.json` y `return_policies.json` del Taller #1.
2.  **Hibridación (RAG + SQL-like):** 
    *   El script `taller2_rag.py` ahora detecta números de seguimiento (ej. ECO1001) usando expresiones regulares y consulta la base de datos JSON original.
    *   Las políticas por categoría que estaban en JSON se han convertido a Markdown para que el sistema RAG pueda realizar búsquedas semánticas sobre ellas, permitiendo consultas más naturales (ej. "¿puedo devolver un cepillo?") en lugar de búsquedas por clave exacta.
3.  **Prompt Unificado:** Se diseñó un prompt que combina el contexto recuperado de documentos con los datos estructurados del pedido, permitiendo que el asistente actúe con conocimiento total de la empresa y del cliente específico.
