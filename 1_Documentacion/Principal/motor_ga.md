# src/motor_ga.py (Módulo 3: motor evolutivo)

**Para qué existe:** ejecutar una corrida completa del AG de permutación, en su variante estática o adaptativa, y escribir un CSV con una fila por generación. Usa DEAP para los operadores.

## Preámbulo

- `creator.create("FitnessMax", ..., weights=(1.0,))`: un solo objetivo, a maximizar. `Individual` es una lista con ese fitness. El `if not hasattr` evita un error si el módulo se importa dos veces.
- `N_PARES_DIV = 100`: pares muestreados para estimar la diversidad.

## Funciones

### `_evaluar(ind, lam)`
Calcula NL y δ **una sola vez** con `metricas`, los guarda en el individuo (`ind.nl`, `ind.delta`) y fija `ind.fitness.values = (fitness,)` (DEAP exige tupla).

### `diversidad(pop, rng)`
Distancia de Hamming media normalizada entre 100 pares al azar: para cada par, la fracción de las 256 posiciones en que difieren. 0 = clones; ≈ 1 = totalmente distintos (dos permutaciones aleatorias difieren en casi todas las posiciones). Usa **su propio generador** (`semilla + 7919`), para que medir la diversidad no consuma números aleatorios de la evolución.

### `explorando(p, cfg)`
La adaptativa está en modo explorar si su torneo vigente es `k_explorar` (y `k_explorar ≠ k`).

### `actualizar_parametros(p, ind, cfg)` (la regla adaptativa)
Función pura: recibe los parámetros vigentes `p = {mutpb, indpb, k}` y los indicadores `ind = {sin_mejora_nl, sin_mejora_delta, div}`, y devuelve parámetros nuevos sin modificar sus argumentos.

```
si está explorando y div ≥ div_rec:            → EXPLOTAR (mutpb, indpb, k de la estática)
si está explorando, o
   (sin_mejora_nl ≥ ventana Y sin_mejora_delta ≥ ventana), o
   div < div_min:                              → EXPLORAR
        mutpb ← min(mutpb·factor, mutpb_max)
        indpb ← min(indpb·factor, indpb_max)
        k     ← k_explorar
si no:                                         → sin cambios
```

La **histéresis** (entrar con `div_min`, salir con `div_rec`) evita que la regla se quede atorada en un modo; la primera versión sin histéresis exploraba ~80 % del tiempo y se comportaba como búsqueda aleatoria.

### `_descendencia(pop, cxpb, mutpb, indpb, k, lam)`
1. Selección por torneo de tamaño `k` (`selTournament`) y copias profundas.
2. Cruce PMX (`cxPartialyMatched`) por parejas con probabilidad `cxpb`; preserva la permutación.
3. Mutación `mutShuffleIndexes` con probabilidad `mutpb`; cada posición se intercambia con probabilidad `indpb`; también preserva la permutación.
4. Evalúa solo los individuos que cambiaron (`not ind.fitness.valid`).

### `correr(semilla, adaptativo, cfg, ruta_csv)`
**Inicialización:** `random.seed(semilla)`, N permutaciones barajadas y evaluadas. Con la misma semilla, ambas variantes (y la búsqueda aleatoria) parten de la misma población. `HallOfFame(1)` guarda el mejor histórico.

**Ciclo `for g in range(G + 1)`:**
1. Mide: mejor individuo, fitness de la población y diversidad.
2. Actualiza contadores (desde `g > 0`): `sin_mejora` (fitness del mejor), `sin_mejora_nl` (mejor NL de la población) y `sin_mejora_delta` (mejor δ de la población).
3. Registra la fila del CSV (ver `Resultados/columnas_csv.md`). En la última generación termina.
4. **Única diferencia entre variantes:** si es adaptativa, llama a `actualizar_parametros`. Al salir de explorar, los contadores de NL y δ se reinician (el estancamiento se mide desde cero).
5. Genera la descendencia con los parámetros vigentes.
6. Elitismo: el mejor histórico reemplaza al peor descendiente.

**Salida:** escribe el CSV (saltos de línea LF) y devuelve el mejor individuo.

## Garantías probadas (`tests/test_motor.py`)

- Con `factor = 1.0` y `k_explorar = k` (control neutro), la adaptativa produce un CSV idéntico al de la estática, salvo la columna `variante`: la única diferencia entre variantes es el lazo.
- La misma semilla da el mismo CSV; semillas distintas dan corridas distintas.
- El elitismo funciona (el mejor siempre sigue en la población) y todo descendiente es una permutación con métricas vigentes.
- La regla respeta los topes, no modifica sus argumentos, no explora si solo NL está estancado y no se queda atorada explorando.
