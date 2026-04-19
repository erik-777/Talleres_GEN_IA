# Fase 2. Evaluación de fortalezas, limitaciones y riesgos éticos

## 2.1 Fortalezas

La principal fortaleza del sistema propuesto es la **reducción del tiempo de respuesta**. Si el 80% de las consultas son repetitivas, automatizar ese bloque permite responder en segundos o minutos en lugar de 24 horas.

Otra fortaleza es la **disponibilidad continua**. El asistente puede operar 24/7, lo que resulta especialmente útil para un e-commerce donde los clientes consultan fuera del horario laboral.

También destaca la **consistencia en las respuestas**. Un sistema guiado por políticas internas reduce variaciones entre agentes y mantiene criterios homogéneos en devoluciones, seguimiento de pedidos y explicación de productos.

Por último, mejora la **productividad del equipo humano**, ya que los agentes dejan de invertir tiempo en preguntas rutinarias y pueden concentrarse en incidencias sensibles o complejas.

## 2.2 Limitaciones

La primera limitación es evidente: **el sistema no debe manejar solo el 20% de casos complejos**. Quejas, reclamos tensos, errores operativos graves o clientes molestos requieren criterio humano. Intentar automatizarlo todo sería una mala idea.

La segunda limitación es la **dependencia de la calidad de los datos internos**. Si la base de pedidos está desactualizada o la política de devoluciones está mal cargada, el modelo responderá mal aunque el prompt esté bien construido.

Otra limitación es que el sistema puede **fallar en lenguaje ambiguo, sarcasmo o contexto emocional**. Puede interpretar mal una consulta híbrida, por ejemplo: “Mi pedido no llega, ya pedí devolución y nadie responde”.

Además, la IA generativa puede dar una respuesta “bien redactada” pero operativamente equivocada. Esa combinación es peligrosa porque aparenta confiabilidad.

## 2.3 Riesgos éticos

El taller pide evaluar alucinaciones, sesgo, privacidad e impacto laboral. Esos riesgos no son accesorios; son parte del núcleo del diseño. 

### Alucinaciones

El modelo podría inventar información sobre un pedido, una fecha de entrega o una política de devolución. Este riesgo es crítico porque afecta la confianza del cliente y puede generar pérdidas o conflictos.

**Mitigación**:

* Obligar al sistema a responder solo con información recuperada de fuentes internas.
* No permitir estimaciones no verificadas.
* Escalar si no existe dato suficiente.

### Sesgo

El modelo puede responder de forma desigual según el lenguaje del usuario, su forma de expresarse, errores ortográficos o patrones presentes en los datos de entrenamiento.

**Mitigación**:

* Revisión periódica de respuestas.
* Pruebas con perfiles diversos.
* Políticas de redacción neutrales.
* Intervención humana en casos sensibles.

### Privacidad de datos

El sistema manejará información sensible como nombre, dirección, historial de compras y estado de pedidos. Exponer esos datos en prompts o registros inseguros sería un error grave.

**Mitigación**:

* Minimización de datos en prompts.
* Enmascaramiento de información sensible.
* Control de acceso.
* Cifrado.
* Auditoría de consultas.
* No usar información personal para entrenamiento sin consentimiento y gobernanza clara.

### Impacto laboral

Automatizar soporte puede percibirse como reemplazo de agentes. Ese enfoque es pobre y además contraproducente.

**Punto crítico**: si la empresa usa la IA solo para reducir personal, Probablemente degradará la atención en los casos complejos. La automatización debe orientarse a **empoderar** al equipo humano, no a eliminarlo indiscriminadamente.

**Mitigación**:

* Redefinir roles hacia supervisión, escalamiento y atención especializada.
* Capacitar al personal.
* Usar la IA como copiloto operativo.
