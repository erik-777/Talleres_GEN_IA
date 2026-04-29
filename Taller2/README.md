# Taller Práctico #2 - Sistema RAG para EcoMarket

Este repositorio contiene la implementación de un sistema de Generación Aumentada por Recuperación (RAG) para optimizar la atención al cliente de EcoMarket.

## Estructura del Proyecto

- `RESPUESTAS.md`: Contiene las respuestas detalladas a las Fases 1 y 2 (Selección de componentes y Base de conocimiento).
- `taller2_rag.py`: Script principal con la implementación del sistema RAG usando LangChain.
- `knowledge_base/`: Carpeta con los documentos que alimentan la base de conocimientos.
- `requirements.txt`: Dependencias necesarias para ejecutar el proyecto.

## Requisitos Previos

1. Tener una cuenta de OpenAI y una `OPENAI_API_KEY`.
2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Para iniciar el sistema y realizar consultas de prueba, ejecuta:
```bash
export OPENAI_API_KEY='tu_api_key_aquí'
python taller2_rag.py
```

El sistema cargará los documentos, creará la base de datos vectorial localmente en `chroma_db/` y responderá a una serie de preguntas de ejemplo sobre políticas y FAQs.
