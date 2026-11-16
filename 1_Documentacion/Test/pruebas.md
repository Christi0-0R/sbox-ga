# Pruebas automáticas (tests/)

Se ejecutan con `python -m pytest -q` desde la raíz. Estado al cierre de la Fase 6: **126 pasan y 1 se salta** (`test_sboxu.py`, que necesita Sage; en el entorno de Sage en Colab pasa).

Además de las pruebas, en las Fases 2b, 4, 5a y 5b se hicieron **pruebas de mutación manuales**: se rompió el código a propósito (sin elitismo, sin histéresis, contadores al revés, Holm mal aplicado, bootstrap no pareado, comparación de hash siempre verdadera, etc.) y se comprobó que alguna prueba fallara. Las mutaciones que sobrevivían dieron lugar a pruebas nuevas.

## Correspondencia con el plan de pruebas del protocolo (5.1.1)

| Nivel del protocolo | Dónde se cubre |
|---|---|
| Unitaria (GF(2⁸), valores conocidos de AES, permutación) | `test_gf256.py` |
| Regresión (NL = 112, δ = 4 en AES) | `test_evaluador.py` |
| Contraste (cero discrepancias con sboxU) | `test_evaluador.py` (interno), `test_sboxu.py`, `test_contraste_final.py` |
| Propiedad (todo descendiente es permutación) | `test_motor.py::test_operadores_preservan_permutacion`, `test_descendencia_tiene_metricas_y_fitness_vigentes` |
| Reproducibilidad (misma semilla, mismo CSV) | `test_motor.py`, `test_correr_todo.py`, `test_aleatoria.py` |
| Integración (corrida corta sin errores) | `test_motor.py::test_corrida_corta_y_valida`, `test_correr_todo.py`, `--smoke` |
| Funcional (cifrar y descifrar con SHA-256 idéntico) | `test_cifrado.py`, `test_cifrar_archivos.py` |

## Archivo por archivo

| Archivo | Pruebas | Qué cubre |
|---|---|---|
| `test_gf256.py` | 4 | Valores de FIPS-197, permutación, inverso, `{57}·{83} = {c1}`. |
| `test_evaluador.py` | 9 | Regresión AES, identidad lineal, filas de la DDT, contraste con `verificacion.py`, fitness, sesgo lineal y probabilidad diferencial. |
| `test_ejemplo_4x4.py` | 7 | La S-box de PRESENT cumple los criterios de Bogdanov et al. (2007, sec. 4.3) y los valores de Walsh de un bit que reporta Ohkuma (2009); la identidad no los cumple. |
| `test_motor.py` | 26 | Reproducibilidad, misma población inicial, esquema del CSV, elitismo, consistencia de métricas, la regla adaptativa caso por caso (estancamiento, diversidad, topes, histéresis, función pura), **identidad con la estática bajo control neutro**, operadores que preservan la permutación. |
| `test_aleatoria.py` | 5 | Búsqueda aleatoria reproducible, mismo punto de partida que el AG, presupuesto y esquema. |
| `test_calibracion_estatica.py` | 4 | Regla de elección y desempate de la rejilla de la estática. |
| `test_calibracion_adaptativa.py` | 5 | Compuerta, regla de elección y desempate de la rejilla de la adaptativa. |
| `test_correr_todo.py` | 12 | Corridas completas, reanudación sin repetir, paralelo = secuencial, no mezcla configuraciones, `config.py` = congelada, modo suplementario aislado. |
| `test_estadistica.py` | 13 | Holm con ejemplo conocido, Cliff, sentido de las pruebas, IC bootstrap pareado y reproducible, mecanismo, análisis de punta a punta y gráficas. |
| `test_contraste_final.py` | 6 | Detecta valores guardados incorrectos y S-boxes que no son permutación; cada implementación cuenta. |
| `test_cifrado.py` | 6 | Ida y vuelta con SHA-256, inversa, valores de AES, rechazo de S-boxes inválidas, archivo de 3 MB. |
| `test_cifrar_archivos.py` | 16 | Muestras deterministas (firma PNG, ELF), regla de la mejor S-box con empates, detección de descifrado corrupto, hash que no coincide y ejecutable que no corre. |
| `test_sboxu.py` | 1 | sboxU coincide en AES (se salta sin Sage). |

## Script de medición

`tests/medir_velocidad.py` no es una prueba: mide los milisegundos por evaluación del fitness (riesgo R2). Laptop: ≈ 10.3 ms; Colab: ≈ 2.8 ms.

```
PYTHONPATH=. python tests/medir_velocidad.py
```
