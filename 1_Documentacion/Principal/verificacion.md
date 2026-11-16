# src/verificacion.py (Módulo 4: segunda implementación)

**Para qué existe:** calcular NL y δ por un camino distinto al de `evaluador.py`, para detectar errores de implementación. Si dos programas escritos de forma distinta coinciden siempre, es poco probable que ambos tengan el mismo error.

## Funciones

| Función | Método | Diferencia con el evaluador |
|---|---|---|
| `delta_directo(sbox)` | Para cada `dx ≠ 0`, cuenta los pares `S(x) ⊕ S(x ⊕ dx)` en una lista, en Python puro. | Sin NumPy, sin armar la DDT completa. |
| `_fwht(v)` | Transformada rápida de Walsh-Hadamard (mariposas, O(n log n)). | El evaluador usa multiplicación matricial. |
| `nl_fwht(sbox)` | Una FWHT por cada función componente `b·S` con `b ≠ 0`; NL = `128 − max|W| / 2`. | Recorre por función componente, no por matriz completa. |
| `metricas_sboxu(sbox)` | Llama a `sboxU.linearity` y `sboxU.differential_uniformity`; NL = `128 − linearity / 2`. | Implementación externa, escrita por otros autores. |

## sboxU

- sboxU 2.x solo funciona con SageMath, por eso no está en `requirements.txt`.
- Se instala en Colab en un entorno aparte (micromamba + Sage de conda-forge), siguiendo `notebooks/colab_verificacion_sboxu.ipynb`.
- `tests/test_sboxu.py` usa `importorskip`: se salta si no hay Sage y pasa cuando sí lo hay.

## Limitación

`evaluador.py` y `verificacion.py` los escribió el mismo equipo. La verificación realmente independiente es sboxU (ver `Experimentos/contraste.md`).
