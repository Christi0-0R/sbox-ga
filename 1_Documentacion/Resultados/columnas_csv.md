# Columnas de los CSV de corridas

Cada corrida (`resultados/<dir>/<variante>_<semilla>.csv`) tiene G + 1 filas: la generación 0 (población inicial) y las G generaciones evolucionadas. Los CSV no se editan a mano. Saltos de línea LF.

| Columna | Qué es |
|---|---|
| `variante`, `semilla` | Identifican la corrida; constantes en todo el archivo. |
| `generacion` | 0 … G. |
| `fit_mejor` | Fitness del mejor individuo histórico (Hall of Fame). Nunca baja (elitismo). Es el valor que entra a la prueba de H1 en la última fila. |
| `fit_max_pob` | Máximo fitness de la población en esa generación. Debe ser igual a `fit_mejor` (prueba del elitismo). |
| `fit_prom` | Fitness promedio de la población. |
| `nl_mejor`, `delta_mejor` | NL y δ del mejor individuo histórico. |
| `nl_max_pob`, `delta_min_pob` | Mejor NL y mejor δ de la población (pueden ser de individuos distintos). Son las señales de los contadores de la adaptativa. |
| `nl_prom`, `delta_prom` | NL y δ promedio de la población. |
| `diversidad` | Distancia de Hamming media normalizada sobre 100 pares (0 = clones, ≈ 1 = muy distintos). |
| `sin_mejora` | Generaciones consecutivas sin que mejore `fit_mejor`. |
| `sin_mejora_nl`, `sin_mejora_delta` | Generaciones consecutivas sin que mejore el mejor NL / el mejor δ de la población. Se reinician al salir de explorar. |
| `mutpb`, `indpb`, `k`, `cxpb` | Parámetros vigentes. En la estática son constantes (0.4, 0.02, 5, 0.9). En la adaptativa, `k = 3` indica modo explorar. |

La búsqueda aleatoria usa un esquema reducido: `variante, semilla, generacion, fit_mejor, fit_max_pob, fit_prom, nl_mejor, delta_mejor, nl_prom, delta_prom`. Ahí `fit_max_pob` es el máximo del lote de N permutaciones de esa "generación" (puede ser menor que `fit_mejor`, que es el mejor acumulado). No tiene diversidad ni parámetros porque no evoluciona.

## Archivos auxiliares de `resultados/final/`

| Archivo | Contenido |
|---|---|
| `meta.json` | Configuración, semillas, commit (`6334e2f`, etiqueta `congelado-v1`), fechas y versión de Python. |
| `entorno.txt` | `pip freeze` del entorno. |
| `sboxes/<variante>_<semilla>.json` | Mejor S-box de la corrida, con NL, δ y fitness. |
| `analisis_salida.txt` | Salida en consola de `analisis/estadistica.py`. |
| `analisis/` | Tablas CSV y gráficas de convergencia. |
