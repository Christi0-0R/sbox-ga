# Documentación de sbox-ga

Explicación de la estructura y de cada archivo del repositorio, al día con el código de la Fase 5b (configuración congelada `congelado-v1`). El README tiene el método, la bitácora y los resultados; aquí se explica **qué hace cada pieza y cómo se conecta con las demás**.

## La idea general

- Una S-box de 8×8 es una tabla de 256 números (una permutación de 0 a 255) que "revuelve" bytes. Es la única pieza no lineal de un cifrado como AES.
- Su calidad se mide con dos números: **NL** (no-linealidad, más alta es mejor) y **δ** (uniformidad diferencial, más baja es mejor). La S-box de AES tiene NL = 112 y δ = 4 y se usa como cota de referencia.
- Hay 256! tablas posibles, así que no se pueden probar todas. Se usa un **algoritmo genético de permutación**: una población de S-boxes que se seleccionan, cruzan y mutan según un fitness `NL − 2·(δ − 4)`.
- Se comparan dos variantes que comparten todo el código salvo una cosa: la **estática** usa parámetros fijos y la **adaptativa** cambia mutpb, indpb y el tamaño de torneo según el estancamiento de NL y δ y la diversidad de la población. Una **búsqueda aleatoria** con el mismo presupuesto sirve como piso de sanidad.

## Flujo de datos

```
config.py ──► motor_ga.py ──► resultados/final/<variante>_<semilla>.csv  ──► analisis/estadistica.py ──► tablas y gráficas
                 │                               │
           evaluador.py                    sboxes/*.json ──► contraste_final.py (evaluador, verificacion, sboxU)
           (NL, δ, fitness)                       └──────────► cifrar_archivos.py ──► resultados/cifrado/
```

## Mapa de esta carpeta

| Archivo | Qué explica |
|---|---|
| `Principal/gf256.md` | Módulo 1: aritmética de GF(2⁸) y S-box de AES |
| `Principal/evaluador.md` | Módulo 2: DDT, espectro de Walsh, NL, δ, fitness y modelo de atacante |
| `Principal/verificacion.md` | Módulo 4: segunda implementación y puente con sboxU |
| `Principal/motor_ga.md` | Módulo 3: AG estático y adaptativo |
| `Principal/cifrado.md` | Módulo 5: sustitución byte a byte (demostrativo) |
| `Principal/config.md` | Parámetros congelados y semillas |
| `Experimentos/calibracion.md` | Fases 3 y 4: calibración de N y G, de la estática y de la adaptativa |
| `Experimentos/correr_todo.md` | Fase 5a: corridas finales y experimento suplementario |
| `Experimentos/contraste.md` | Verificación cruzada con sboxU |
| `Experimentos/cifrado_archivos.md` | Fase 5b: cifrado de archivos reales |
| `Analisis/estadistica.md` | Módulo 6: pruebas estadísticas, tablas y gráficas |
| `Resultados/columnas_csv.md` | Qué significa cada columna de los CSV de corridas |
| `Resultados/Prelim/estatica_1.md` | Histórico: CSV de la Fase 2 (N = 30, G = 50), ya no vigente |
| `Test/pruebas.md` | Qué cubre cada archivo de pruebas |
| `Referencias/literatura_nl_delta.md` | Valores de NL y δ reportados en la literatura, para la discusión |

## Correspondencia con el protocolo

| Protocolo | Código |
|---|---|
| Módulo 1, Álgebra de GF(2⁸) (OE3) | `src/gf256.py` |
| Módulo 2, Evaluador criptográfico (OE3) | `src/evaluador.py` |
| Módulo 3, Motor evolutivo (OE4) | `src/motor_ga.py` |
| Módulo 4, Verificación cruzada (OE6) | `src/verificacion.py`, `experimentos/contraste_sboxu.py`, `experimentos/contraste_final.py` |
| Módulo 5, Cifrado de archivos binarios (OE6) | `src/cifrado.py`, `experimentos/cifrar_archivos.py` |
| Módulo 6, Análisis experimental (OE5) | `analisis/estadistica.py` |

## Archivos históricos

Siguen en el repositorio para trazabilidad, pero pertenecen a la Fase 2 y usan la configuración vieja:

- `experimentos/prelim_estatica.py`, `experimentos/calibracion.py`
- `analisis/graficas_prelim.py`, `analisis/resumen_prelim.py`, `analisis/prelim_estatica.png`
- `resultados/archivo_v1/`

`analisis/comprobaciones.py` comprueba que las primeras 100 generaciones del experimento suplementario (G = 300) sean idénticas a las corridas finales.
