# estatica_1.csv

### Qué es cada columna

| Columna | Qué es
| --- | ---
| variante, semilla	| Identifican la corrida. Constantes en todo el archivo.
| generacion	| 0 es la población inicial aleatoria; 1 a 50 son las generaciones evolucionadas (51 filas en total).
| fit_mejor	| Fitness del mejor individuo histórico (el del HallOfFame). Nunca baja gracias al elitismo.
| fit_prom	| Fitness promedio de toda la población en esa generación.
| nl_mejor, delta_mejor	| NL y δ del mejor individuo.
| diversidad	| Distancia de Hamming media normalizada (0 = clones, ~1 = muy distintos).
| sin_mejora	| Generaciones consecutivas sin que el mejor mejore.
| mutpb, cxpb	| Probabilidades vigentes. En la estática son constantes (0.2 y 0.9).


### La historia de esta corrida

1. Punto de partida (gen. 0). Diversidad ≈ 0.996: dos permutaciones aleatorias coinciden en ~1 de 256 posiciones, o sea, casi totalmente distintas. El mejor ya tiene fitness 84 (NL = 96, δ = 10). Es normal: una permutación aleatoria típica ronda NL 90-98 y δ 10-12, así que el AG parte de un nivel decente.

2. Colapso de diversidad (gen. 0 a 10). La diversidad cae de 0.996 a 0.099 en solo 10 generaciones. La causa es la selección por torneo (k = 3) con N = 30 más PMX con cxpb = 0.9: los padres mejores se copian y se cruzan entre sí, así que la población se llena de variantes de unos pocos individuos. Para la gen. 10 casi son clones.

3. Una sola mejora (gen. 13). El fitness sube de 84 a 86 (NL 96 → 98). Pasa cuando la diversidad ya estaba en ~0.1, es decir, la mutación encontró una mejora local sobre una población casi uniforme.

4. Estancamiento (gen. 13 a 50). Fitness fijo en 86 durante 37 generaciones: sin_mejora llega a 37 y la diversidad se queda entre 0.02 y 0.04. Esto es convergencia prematura, justo el problema de tu protocolo.

5. Dos detalles curiosos:

- fit_prom (~85.5) queda muy cerca de fit_mejor (86): casi toda la población es el élite o parientes cercanos.
- Los sin_mejora de las gen. 1 a 12 cuentan 1, 2, ..., 12 y se reinician en 0 en la 13 cuando el fitness sube. El contador funciona como esperabas.

### Qué dice esto 

- δ = 10 nunca cambia. Toda la mejora vino de NL (96 → 98), como anotaste. Esto apoya tu “límite” en la evaluación conceptual: δ es un máximo, cambiarlo exige mover todas las celdas altas de la DDT, y la mutación aleatoria casi nunca lo logra. Tu pendiente de “contar celdas en el máximo” ataca justo esto.
- Evidencia concreta de la hipótesis de partida: estancamiento total del fitness con diversidad ≈ 0.03. Esta corrida es un buen ejemplo para citar en el texto (por ejemplo “en la semilla 1, el fitness se estanca en 86 desde la generación 13 mientras la diversidad cae de 0.996 a ~0.03”).
- Lectura crítica útil: como la diversidad ya está en ~0.1 en la gen. 10, una adaptativa que suba mutpb después de detectar estancamiento (ventana 5 u 8) reacciona tarde: el daño ya está hecho. Eso respalda tu observación de que div_min pesa poco y manda ventana, y es un argumento para rediseñar el lazo (por ejemplo, reaccionar a la velocidad de caída de la diversidad, no solo a un umbral).

