# Fase 1. Selección y justificación del modelo de IA

## 1.1 Modelo propuesto

La solución más adecuada para EcoMarket es una **arquitectura híbrida basada en un LLM general integrado con fuentes internas de información mediante recuperación contextual**. En términos prácticos, esto significa usar un modelo de lenguaje para generar respuestas naturales, pero no dejarlo “inventar” información crítica. En lugar de eso, el sistema debe consultar primero una base de datos interna con pedidos, políticas de devolución y catálogo de productos, y luego construir la respuesta usando esos datos como contexto.

La decisión no debería ser “usar un LLM gigante y ya”, porque eso sería técnicamente débil para un caso donde el dato factual importa más que la creatividad. Tampoco conviene, como primera opción, entrenar o afinar un modelo desde cero solo con datos de la empresa, porque el problema principal no es lingüístico sino de acceso confiable a información operacional actualizada.

## 1.2 Tipo de arquitectura

La arquitectura propuesta sería:

1. **Canales de entrada**: chat web, correo y redes sociales.
2. **Clasificador de intención**: identifica si la consulta es sobre estado del pedido, devolución, producto, queja o caso complejo.
3. **Motor de recuperación de información**:

   * base de pedidos,
   * políticas de devolución,
   * catálogo de productos,
   * preguntas frecuentes.
4. **LLM generador de respuesta**: redacta la respuesta en lenguaje claro y amable a partir de la información recuperada.
5. **Módulo de escalamiento humano**: transfiere el caso a un agente si detecta:

   * queja,
   * conflicto,
   * frustración,
   * problema técnico no resuelto,
   * ausencia de datos confiables,
   * alta incertidumbre en la respuesta.
6. **Registro y monitoreo**: almacena consultas, respuestas, errores, escalaciones y retroalimentación.

## 1.3 ¿Por qué esta solución y no otra?

### Opción 1: LLM general puro

No es la mejor opción. Tiene buena fluidez, pero puede alucinar estados de pedidos, inventar plazos o confundir políticas. Para atención al cliente eso es un error serio.

### Opción 2: modelo pequeño afinado

Puede ser más barato en inferencia, pero exige datos curados, mantenimiento y ciclos de reentrenamiento. Además, aunque esté afinado, seguiría necesitando acceso en tiempo real a pedidos y políticas actualizadas. Afinar no sustituye la consulta a fuentes vivas.

### Opción 3: solución híbrida con recuperación contextual

Es la mejor alternativa porque combina:

* Precisión factual para consultas repetitivas.
* Lenguaje natural para la interacción.
* Menor riesgo de invención.
* Mejor escalabilidad.
* Integración más simple con sistemas existentes.

## 1.4 Justificación técnica

### Costo

Una solución híbrida reduce costos operativos porque automatiza el 80% de las consultas repetitivas sin intentar resolver por IA los casos donde fallará más. Eso evita sobrediseñar el sistema.

### Escalabilidad

El sistema puede atender múltiples consultas simultáneamente 24/7. A medida que crece EcoMarket, se añaden más fuentes de datos y reglas sin rehacer todo el modelo.

### Facilidad de integración

La empresa ya tiene información estructurada: pedidos, devoluciones y catálogo. El valor está en conectarla al asistente, no en construir inteligencia desde cero.

### Calidad de respuesta

El LLM aporta claridad, tono y personalización. La base de datos aporta exactitud. Separar ambos roles mejora el resultado final.

## 1.5 Conclusión de la Fase 1

Se propone una **solución híbrida LLM + recuperación de información + escalamiento humano**. No se recomienda depender de un modelo generativo aislado, porque la precisión operativa es prioritaria. La IA debe actuar como primer nivel de atención para consultas repetitivas, mientras que los casos complejos deben pasar a agentes humanos. Esta propuesta responde de forma directa al escenario descrito para EcoMarket y a los criterios de costo, escalabilidad, integración y calidad exigidos por el taller. 
