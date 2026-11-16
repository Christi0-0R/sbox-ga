# Verificación cruzada con sboxU (Módulo 4)

**Para qué existe:** cumplir el criterio del protocolo de "cero discrepancias" entre el evaluador propio y una herramienta pública (OE6).

## Tres implementaciones

| Métrica | `src/evaluador.py` | `src/verificacion.py` | sboxU 2.0 |
|---|---|---|---|
| δ | DDT vectorizada con NumPy | Conteo directo en Python puro | `differential_uniformity` |
| NL | Walsh por multiplicación matricial | FWHT por función componente | `128 − linearity / 2` |

## experimentos/contraste_sboxu.py

- Contrasta AES y 50 permutaciones aleatorias (semilla 0).
- Resultado en Colab con Sage: **51/51 coinciden**.

## experimentos/contraste_final.py

- Lee `resultados/<dir>/sboxes/*.json` y recalcula NL, δ y fitness de cada S-box final con las tres implementaciones; los compara con lo guardado en la corrida.
- Si sboxU no está disponible, avisa y hace solo el contraste interno; el modo de verificación final se detiene con error para no dar por bueno un contraste parcial.
- Resultado: **200/200 coinciden** (100 estáticas + 100 adaptativas).

## Cómo se instala sboxU

`notebooks/colab_verificacion_sboxu.ipynb`: micromamba con Sage de conda-forge en un entorno aparte, luego `python -m pip install --no-build-isolation` de sboxU con el Python de ese entorno. Ahí corre `pytest` (con `test_sboxu.py` ya sin saltarse) y los dos contrastes. La evidencia está en `evidencia/colab_2026-11-14/`.

## Reproducibilidad entre máquinas

En el mismo notebook se recalcularon 3 semillas (1000 a 1002) × 3 variantes en Colab con la configuración congelada: 15/15 archivos idénticos byte a byte a los de la laptop.
