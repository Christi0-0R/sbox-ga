# motor_ga.py (el corazón)

### Preámbulo

- `creator.create("FitnessMax", ..., weights=(1.0,))`: fitness a maximizar, un solo objetivo. Individual es una lista con ese fitness. El if not hasattr evita error si el módulo se importa dos veces.
- `_evaluar(ind)`: DEAP exige que el fitness sea una tupla, por eso (fitness(ind),).

### diversidad(pop, rng)

Toma 100 pares al azar de la población y calcula, para cada par, la fracción de posiciones (de 256) donde difieren (distancia de Hamming normalizada). Promedia. 0 = clones; ~1 = totalmente distintos (dos permutaciones aleatorias difieren en casi todas las posiciones, por eso la gen. 0 da ≈1.0). Usa su propio rng para que medir la diversidad no consuma números aleatorios de la evolución: así la estática y la adaptativa siguen idénticas hasta que el lazo intervenga.

### actualizar_parametros(mutpb, sin_mejora, div, cfg)

El lazo adaptativo (placeholder). Si hay estancamiento (sin_mejora >= ventana) o poca diversidad (div < div_min), sube mutpb multiplicándolo por factor (con tope mutpb_max). Si no, lo baja dividiendo por factor (con piso en el mutpb base).

Ojo, esto conecta con tu hallazgo de calibración: con div_min = 0.5 y la diversidad cayendo rápido, la condición casi siempre se cumple, mutpb se queda pegado al tope y la adaptativa se vuelve una estática con mutpb ≈ 0.8. Por eso dices que hay que rediseñar el lazo.

### correr(semilla, adaptativo, cfg, ruta_csv): una corrida completa

**Inicialización**

- random.seed(semilla): reproducibilidad.
- rng_div: generador aparte (semilla + 7919) para la diversidad.
- Crea N individuos como permutaciones barajadas de 0..255 y los evalúa. Como la semilla es la misma, ambas variantes arrancan con la misma población inicial (tu prueba lo verifica).
- hof = HallOfFame(1): guarda el mejor individuo histórico.

**Variables de control**: cxpb, mutpb, mejor_hist (mejor fitness visto) y sin_mejora (contador de estancamiento).

### Ciclo for g in range(G+1) (G+1 porque incluye la generación 0):

1. Medición: toma el mejor, los fitness, y la diversidad.
2. Contador de estancamiento: si el mejor superó al histórico, lo actualiza y reinicia el contador; si no, suma 1. (Solo desde g > 0.)
3. Registro: guarda una fila con todas las métricas (la que va al CSV: variante, semilla, generación, fitness mejor/promedio, NL, δ, diversidad, sin_mejora, mutpb, cxpb). Si es la última generación, break.
4. Única diferencia entre variantes: si es adaptativa, actualiza mutpb.
5. Selección: torneo de tamaño k (elige k al azar y gana el mejor), y copias profundas para no modificar a los padres.
6. Cruce: recorre las parejas (off[0],off[1]), (off[2],off[3])...; con prob. cxpb aplica PMX (cruce parcialmente mapeado, que garantiza hijos que siguen siendo permutaciones) y borra el fitness para forzar reevaluación.
7. Mutación: con prob. mutpb aplica mutShuffleIndexes (intercambia posiciones con prob. indpb, también preserva la permutación).
8. Reevaluación solo de los que cambiaron (if not ind.fitness.valid), para ahorrar cómputo.
8. Elitismo: ordena la nueva generación de peor a mejor y reemplaza al peor por el mejor histórico, para que nunca se pierda lo ganado. Actualiza pop y hof.

Salida: escribe el CSV (crea la carpeta si no existe) y devuelve el mejor individuo.##