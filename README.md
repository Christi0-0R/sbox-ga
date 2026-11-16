# sbox-ga

Algoritmo genético de permutación (estático vs. retroalimentación adaptativa) para optimizar S-boxes de 8x8 sobre GF(2^8), con la no-linealidad (NL) y la uniformidad diferencial (δ) como métricas.

Proyecto de investigación tecnológica, Taller de Investigación II.
Instituto Tecnológico de Morelia (TecNM), Departamento de Sistemas y Computación.
Línea: Seguridad e Infraestructura y Servicios.

**Autores:** Christian Regina Rodríguez Magaña, Leonardo Blanco Ambriz
**Asesor:** Juan Jesús Ruiz Lagunas

## 1. Qué es este proyecto

Se estudia si agregar retroalimentación adaptativa a un algoritmo genético de permutación mejora el compromiso entre NL y δ, frente a un algoritmo genético estático equivalente. La S-box de AES (NL = 112, δ = 4) se usa como cota de referencia y calibración, no como objetivo a superar.

**Hipótesis (H1):** la variante adaptativa obtiene mayor NL, menor δ y mayor fitness final que la estática, con la misma función de fitness, el mismo tamaño de población y el mismo número de generaciones.

## 2. Marco metodológico

- **Enfoque:** Ciencia del Diseño (Design Science Research), modelo DSRM de Peffers et al. (2007). En el estándar ACM SIGSOFT esta categoría se llama "Engineering Research".
- **Estándar de referencia:** ACM SIGSOFT Empirical Standards, "Engineering Research (Design Science)".

### 2.1 Artefacto

El artefacto es un modelo (March y Smith, 1995): la representación de la evolución de S-boxes de 8x8 sobre GF(2^8) como un proceso de optimización sobre permutaciones, con una función de fitness mono-objetivo (NL y δ) y un mecanismo de retroalimentación adaptativa que reorienta la búsqueda a partir del estado de la población.

Se implementa en dos versiones del mismo código:

| Versión | Descripción | Rol |
|---|---|---|
| Base (estática) | AG de permutación con parámetros fijos durante toda la ejecución | Línea base de control |
| Extendida (adaptativa) | El mismo AG con un lazo que usa el resultado de los ataques simulados (estancamiento de NL y de δ) y la diversidad de la población para alternar entre explotar (parámetros de la estática) y explorar (más mutación, menos presión de selección) | Contribución propuesta |

La única diferencia entre versiones es el lazo de control de parámetros. DEAP, NumPy y el evaluador criptográfico son componentes de apoyo, no la contribución.

**Modelo de atacante.** El ataque se modela mediante NL y δ, que corresponden al mejor ataque lineal y al mejor ataque diferencial posibles contra cada S-box. El sesgo del mejor ataque lineal es (128 − NL)/256 y la probabilidad del mejor ataque diferencial es δ/256 (AES: 0.0625 y 0.0156). En cada generación ambos ataques se aplican a la población; la variante adaptativa reacciona a su resultado y la estática no. El atacante es **simulado mediante métricas**: no se implementa un ataque criptoanalítico completo.

### 2.2 Método de evaluación empírica

Se usa una **simulación cuantitativa** (tipo iv del estándar ACM SIGSOFT): el artefacto se evalúa en un entorno computacional artificial frente a un artefacto competidor, la versión estática.

- 100 ejecuciones independientes por variante, más 100 de búsqueda aleatoria como referencia de sanidad, con las mismas 100 semillas (1000 a 1099) para todas.
- Misma función de fitness, tamaño de población (N = 100) y número de generaciones (G = 100).
- Prueba principal: Mann-Whitney unilateral sobre NL (mayor), δ (menor) y fitness final (mayor), con corrección de Holm sobre las tres pruebas.
- Sensibilidad: Wilcoxon pareado por semilla. Efecto: diferencia de medias con IC 95 % (bootstrap pareado) y delta de Cliff.
- Referencias: búsqueda aleatoria con el mismo presupuesto (atributo 7 del estándar ACM) y la S-box de AES (NL = 112, δ = 4) como cota.

No es un experimento controlado en el sentido del estándar (tipo iii), que requiere participantes humanos.

## 3. Notación

| Símbolo | Significado |
|---|---|
| π | S-box representada como permutación de {0, ..., 255} |
| NL(π) | No-linealidad, calculada con el espectro de Walsh (LAT = Walsh/2) |
| δ(π) | Uniformidad diferencial: máximo de la DDT excluyendo la fila dx = 0 |
| N | Tamaño de la población |
| G | Número de generaciones |
| LAMBDA | Peso con que δ penaliza el fitness |
| k, mutpb, indpb, cxpb | Tamaño de torneo, probabilidad de mutación, probabilidad de intercambio por posición y probabilidad de cruce |
| ventana, div_min, div_rec, factor | Umbrales de la variante adaptativa: generaciones sin mejora, diversidad mínima, diversidad con la que se termina de explorar y factor de ajuste |
| Sesgo lineal | (128 − NL)/256: sesgo del mejor ataque lineal |
| Prob. diferencial | δ/256: probabilidad del mejor ataque diferencial |

## 4. Supuestos explícitos

1. La S-box de AES es una cota de referencia (NL = 112, δ = 4), no un objetivo a superar.
2. El fitness es mono-objetivo y agregado: NL menos LAMBDA por (δ - 4). Es una decisión metodológica, no una afirmación de que sea la mejor forma de combinar ambas métricas.
3. N = 100 y G = 100 (calibración de la Fase 3), iguales en ambas variantes.
4. LAMBDA = 2.0 es **fijo**: decisión metodológica tomada antes de calibrar (riesgo R7), no entra en ninguna rejilla. Los parámetros base (mutpb = 0.4, indpb = 0.02, k = 5) se calibraron para la estática y los umbrales de la adaptativa (ventana = 20, div_min = 0.05, factor = 2.0) para la adaptativa, con el mismo presupuesto (27 configuraciones × 20 semillas preliminares cada una). Los topes y k_explorar se fijaron antes de calibrar. Todo se congela antes de las corridas finales y no se modifica después de ver sus resultados.
5. Las corridas preliminares usan las semillas 1 a 20; las finales, 1000 a 1099.
6. Con n = 100 por variante, el diseño detecta con 80 % de potencia efectos de d ≈ 0.40 (bilateral) o 0.36 (unilateral). Diferencias menores podrían no detectarse.
7. Las rejillas de calibración fueron acotadas. El óptimo de la estática quedó en el borde (mutpb y k máximos) y el de la adaptativa también (ventana máxima, div_min mínimo, factor máximo). Es una limitación declarada.
8. La probabilidad de cruce no se adapta; se adaptan mutpb, indpb y k.
9. El atacante es simulado mediante NL y δ (ver 2.1).
10. El fitness toma pocos valores distintos (casi siempre pares), lo que produce muchos empates en las pruebas.

## 5. Estructura del repositorio

```
sbox-ga/
├── README.md
├── requirements.txt
├── demo_cifrado.py               # Ejemplo con un mensaje corto: cifra y descifra con una S-box final
│
├── src/
│   ├── gf256.py                  # Módulo 1: álgebra de GF(2^8) y S-box AES
│   ├── evaluador.py              # Módulo 2: DDT, LAT/Walsh, NL, delta,
│   │                             #         sesgo_lineal, prob_diferencial y fitness
│   ├── motor_ga.py               # Módulo 3: AG estático y adaptativo
│   ├── verificacion.py           # Módulo 4: segunda implementación (FWHT, conteo directo)
│   └── cifrado.py                # Módulo 5: sustitución byte a byte con una S-box (demostrativo, no seguro)
│
├── tests/                        # Pruebas automáticas (pytest)
│
├── experimentos/
│   ├── config.py                 # Parámetros congelados, comunes a ambas variantes
│   ├── correr_todo.py            # Corridas finales (3 variantes x 100 semillas) y modo --suplementario
│   ├── baseline_aleatoria.py     # Búsqueda aleatoria con el mismo presupuesto
│   ├── calibracion_NG.py         # Fase 3: (N, G) vs. búsqueda aleatoria
│   ├── calibracion_estatica.py   # Fase 3: rejilla de la estática (27 configuraciones)
│   ├── calibracion_adaptativa.py # Fase 4: rejilla de la adaptativa (27 configuraciones)
│   ├── contraste_sboxu.py        # Contraste de 51 S-boxes (AES + 50 aleatorias) con sboxU
│   ├── contraste_final.py        # Contraste de las S-boxes finales de cada corrida
│   ├── generar_muestras.py       # Fase 5b: crea los archivos de ejemplo (texto, PNG, ELF mínimo, vacío)
│   └── cifrar_archivos.py        # Fase 5b: cifra y descifra con la mejor estática, la mejor adaptativa y AES
│
├── ejemplos/                     # Fase 5b: archivos de prueba para el cifrado (4 archivos pequeños)
│
├── resultados/
│   ├── archivo_v1/               # Corridas del motor anterior (historial)
│   ├── calib_NG/                 # Calibración de N y G
│   ├── calib_estatica/           # Calibración de la estática
│   ├── calib_adaptativa/         # Calibración de la adaptativa
│   ├── final/                    # 300 corridas finales, S-boxes (sboxes/), meta.json y análisis
│   ├── suplementario_G300/       # Experimento exploratorio (G = 300, n = 40)
│   └── cifrado/                  # Fase 5b: cifrado_archivos.csv y comparacion_sboxes.csv
│
├── analisis/
│   ├── estadistica.py            # Módulo 6: pruebas, tablas y gráficas
│   └── comprobaciones.py         # Comprobaciones de coherencia de los resultados
│
├── evidencia/                    # Salidas de las verificaciones hechas en Colab (sboxU, reproducibilidad)
│
├── 1_Documentacion/              # Explicación de cada archivo y referencias (ver INDICE.md)
│
└── notebooks/
    ├── colab_main.ipynb                 # Clona el repositorio y ejecuta en Google Colab
    ├── colab_fase5_correr_todo.ipynb    # Corridas finales en Colab
    └── colab_verificacion_sboxu.ipynb   # Instala Sage y sboxU y verifica los resultados finales
```

## 6. Entorno

- **Laptop (desarrollo):** Python 3.10 o superior (se desarrolla con 3.14), entorno virtual `.venv`.
- **Google Colab (experimentos):** la versión de Python y de cada librería se guarda en `entorno.txt` de cada corrida.
- **Dependencias:** ver `requirements.txt` (numpy, scipy, pandas, matplotlib, deap, pytest).

### Instalación

```
git clone https://github.com/Christi0-0R/sbox-ga.git
cd sbox-ga
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Pruebas

```
python -m pytest -q
```

### Uso en Google Colab

Hay notebooks en `notebooks/`. `colab_main.ipynb` monta Google Drive, clona el repositorio, instala las dependencias y ejecuta los scripts; los CSV se escriben a Drive para poder reanudar si la sesión se desconecta. `colab_fase5_correr_todo.ipynb` lanza las corridas finales. `colab_verificacion_sboxu.ipynb` instala Sage y sboxU en un entorno aparte (micromamba, con su propio Python), corre las pruebas y el contraste de las S-boxes finales con sboxU, recalcula tres semillas para comparar byte a byte con los resultados de la laptop y guarda la evidencia en Drive.

### Ejecución de scripts

La forma recomendada, igual en laptop y en Google Colab, es indicar la raíz del repositorio como PYTHONPATH:

Linux / Mac / Git Bash:
```
PYTHONPATH=. python tests/medir_velocidad.py
```

Windows PowerShell:
```
$env:PYTHONPATH = "."
python tests/medir_velocidad.py
```

Windows CMD:
```
set PYTHONPATH=.
python tests/medir_velocidad.py
```

Google Colab (en una celda):
```
%env PYTHONPATH=.
!python tests/medir_velocidad.py
```

Nota: la forma "python -m tests.medir_velocidad" no es la recomendada, porque requiere que existan archivos __init__.py en las carpetas del proyecto y falló en Colab. Los tests se ejecutan siempre con:
```
python -m pytest -q
```

### Reproducir los resultados

Desde la raíz del repositorio y con el entorno instalado:

```
python -m experimentos.correr_todo                    # 300 corridas finales (reanudable)
python -m experimentos.correr_todo --suplementario    # experimento exploratorio: G = 300, 40 semillas
python -m analisis.estadistica resultados/final       # tablas y gráficas del análisis
python -m experimentos.contraste_final resultados/final   # recalcula NL y delta de las S-boxes finales
python -m experimentos.generar_muestras               # crea ejemplos/ (archivos de prueba)
python -m experimentos.cifrar_archivos                # cifra y descifra archivos con las S-boxes finales (Fase 5b)
PYTHONPATH=. python demo_cifrado.py                   # ejemplo con un mensaje corto (ilustrativo)
```

`correr_todo.py` es reanudable: si se interrumpe, se vuelve a lanzar el mismo comando y retoma donde iba. Se niega a correr si `config.py` no coincide con la configuración congelada o si el directorio contiene corridas de otra configuración. Con `--smoke` hace una prueba rápida (3 semillas, N = 20, G = 10) que no es resultado. Cada ejecución guarda `meta.json` (configuración, commit, fecha) y `entorno.txt` (`pip freeze`).

## 7. Verificación cruzada (Módulo 4)

El protocolo contempla sboxU como contraste independiente de NL y δ. Se verificó con sboxU 2.0, que solo funciona con SageMath: se instala en Google Colab en un entorno aparte (micromamba, Sage de conda-forge) siguiendo `notebooks/colab_verificacion_sboxu.ipynb`. Por eso no está en requirements.txt, y `tests/test_sboxu.py` se salta cuando no hay Sage (`importorskip`).

Se contrastan tres implementaciones:

| Métrica | Evaluador (src/evaluador.py) | Contraste interno (src/verificacion.py) | sboxU |
|---|---|---|---|
| δ | DDT vectorizada con NumPy | Conteo directo de pares en Python puro | `differential_uniformity` |
| NL | Espectro de Walsh por multiplicación matricial | Transformada rápida de Walsh-Hadamard por función componente | `128 − linearity / 2` |

Resultados:
- `experimentos/contraste_sboxu.py`: AES y 50 permutaciones aleatorias (semilla 0): 51/51 coinciden.
- `experimentos/contraste_final.py`: las 200 S-boxes finales del AG (estática y adaptativa) coinciden en NL, δ y fitness con lo guardado en cada corrida: 200/200 con sboxU. Se detiene con error si corre sin sboxU, para no dar por bueno un contraste parcial.

Limitación: el evaluador y `verificacion.py` los escribió el mismo equipo, por lo que sboxU aporta la verificación realmente independiente.

---

## 8. Estado del proyecto

- [x] Fase 0: repositorio, entorno local, entorno de Colab y pruebas funcionando
- [x] Fase 1: álgebra de GF(2^8) y evaluador, con regresión contra AES (NL = 112, δ = 4)
- [x] Fase 2a: motor evolutivo (estático, corridas preliminares, adaptativo inicial)
- [x] Fase 2b: correcciones del motor y de las pruebas
- [x] Fase 3: calibración de N, G y de la estática (compuerta contra búsqueda aleatoria)
- [x] Fase 4: adaptativa rediseñada, modelo de atacante, calibración y Módulo 6
- [x] Fase 5a: corridas finales, contraste con sboxU y experimento suplementario
- [x] Fase 5b: cifrado de archivos binarios con las S-boxes generadas
- [ ] Fase 6: análisis de resultados y documento final

## 8.1 Bitácora de fases

### Fase 1: álgebra de GF(2^8) y evaluador

**Fecha:** 31 de octubre, 2026

**Rama** fase-1-gf256-evaluador

**Responsables:** Christian Regina Rodríguez Magaña

**Revisión:** SIN REVISION

**Qué se implementó**
- src/gf256.py: multiplicación en GF(2^8) módulo x^8+x^4+x^3+x+1 (0x11B), inverso multiplicativo, transformación afín y S-box de AES.
- src/evaluador.py: DDT, espectro de Walsh (LAT = Walsh/2), NL, δ y fitness mono-objetivo.
- src/verificacion.py: segunda implementación independiente de NL y δ.
- analisis/ejemplo_4x4.py: ejemplo didáctico de DDT con una S-box de 4 bits (no es parte de la evaluación).
- pytest.ini: configura pytest para encontrar el paquete src.

**Pruebas** (python -m pytest -q)
- 10 pruebas pasan.
- Las 10 pruebas también pasan en Google Colab (rama fase-1-gf256-evaluador).
- Regresión con AES: NL = 112 y δ = 4.
- Valores conocidos de la S-box de AES (S[0x00]=0x63, S[0x01]=0x7C, S[0x53]=0xED) y ejemplo {57}·{83} = {c1} de FIPS-197.
- Contraste de ambos evaluadores: cero discrepancias en AES y en 10 permutaciones aleatorias.
- Cada fila de la DDT suma 256.

**Medición de velocidad (riesgo R2)**

| Entorno | Python | ms por evaluación | 90,000 evaluaciones |
|---|---|---|---|
| Laptop: Alienware x14 R2, CPU: Intel Core i7-13620H (13th Gen, 10 núcleos, 16 hilos). | 3.14 | 10.32 | aprox. 15.5 min |
| Google Colab | 3.13.18 | 2.84 | aprox. 4.3 min |

Comando usado: %env PYTHONPATH=. y !python tests/medir_velocidad.py

**Supuestos y decisiones**
- inv(0) = 0, por convención de AES.
- LAMBDA = 2.0 era provisional en esta fase. Después se decidió dejarlo fijo, sin calibrar (Fase 3, riesgo R7). Nota: aquí se hablaba de 60 corridas finales (valor inicial); luego se amplió a 300 corridas (100 semillas × 3 variantes), ver Fase 5a.
- La DDT 4x4 usa la S-box de PRESENT (Bogdanov et al., 2007). Resuelto en la Fase 6: el artículo no publica la DDT completa, así que se comprueban sus criterios de diseño (sección 4.3).

**Hito:** regresión con AES aprobada, por lo que se puede avanzar a la Fase 2.

**Pendientes heredados**
- Definir con el asesor cómo se hará el contraste con sboxU (requiere Sage). Resuelto en la Fase 5a.
- Agregar como referencia valores de NL y δ reportados en la literatura (Picek et al., 2016; Clark et al., 2004), extraídos directamente de los artículos. Resuelto en la Fase 6 (parcial: el valor de Picek et al. falta confirmarlo en el artículo).

---

### Fase 2a: motor evolutivo

**Fecha:** 5 de noviembre, 2026

**Rama:** fase-2-motor

**Responsables:** Christian Regina Rodríguez Magaña

**Revisión:** SIN REVISION

**Nota:** los valores de esta fase (N = 30, G = 50, semillas finales 1000 a 1029, 60 corridas finales) son valores iniciales; se cambiaron en las fases 3 y 5a (N = 100, G = 100, semillas 1000 a 1099, 300 corridas finales).

**Atributos del estándar ACM SIGSOFT que cubre:** descripción del artefacto (1), supuestos explícitos (8), evaluación conceptual (3, pendiente).

**Qué se implementó**
- experimentos/config.py: parámetros compartidos (N = 30, G = 50, cxpb, mutpb, indpb, k, parámetros del lazo adaptativo), semillas finales (1000 a 1029) y semillas preliminares (1 a 5).
- src/motor_ga.py: AG de permutación con DEAP (torneo, PMX, mutShuffleIndexes, elitismo). Una sola base de código para ambas variantes; la única diferencia es la llamada a actualizar_parametros.
- La diversidad se estima como distancia de Hamming media normalizada sobre 100 pares muestreados, con un generador aleatorio independiente para no alterar la secuencia de la evolución.
- experimentos/prelim_estatica.py, experimentos/calibracion.py, analisis/graficas_prelim.py, analisis/resumen_prelim.py.

**Pruebas** (python -m pytest -q)
- 15 pruebas pasan (10 de la fase 1 y 5 del motor).
- Corrida válida (el mejor es permutación), reproducibilidad (misma semilla, mismo CSV), la adaptativa corre, ambas variantes parten de la misma población inicial, y PMX y mutación preservan la permutación en 300 repeticiones.
- Probado en Google Colab.

**Tiempos**
- Corrida de 50 generaciones con N = 30: 1.8 a 2.1 s (la primera, 7.3 s por arranque en frío). Estimación de las 60 corridas finales: unos 2 minutos.
- Calibración (14 configuraciones x 5 semillas, aprox. 70 corridas): unos 30 s (estimado, no cronometrado). Laptop, Python 3.14.

**Resultados de las corridas preliminares de la estática (semillas 1 a 5)**
- Fitness final: 86.0 en las 5 corridas. NL final = 98 y δ = 10 en todas.
- La diversidad pasa de aprox. 1.0 (generación 0) a 0.02 a 0.04 hacia la generación 25: convergencia prematura observada en los datos.
- δ no cambió en ninguna corrida: toda la mejora vino de NL.

**Calibración preliminar (semillas 1 a 5)**
- 14 configuraciones (2 estáticas de control y 12 adaptativas con div_min en {0.05, 0.1, 0.2, 0.5} y ventana en {3, 5, 8}).
- Fitness entre 85.6 y 86.4 en todas; diferencias dentro del ruido con 5 semillas. δ = 10 casi siempre.
- La regla adaptativa inicial mantiene mutpb cerca del tope (0.67 a 0.79) y se comporta como una estática con mutpb = 0.8 (diversidad media 0.26 a 0.43 frente a 0.445). Con ese diseño, una mejora no podría atribuirse a la retroalimentación.
- Con div_min entre 0.05 y 0.2 los resultados son casi idénticos: el umbral de diversidad pesa poco y manda ventana.

**Supuestos y decisiones**
- Las semillas 1 a 5 se usan solo para calibrar; no son evidencia de H1.
- No se eligió configuración por diferencias de 0.4 puntos de fitness (ruido); el criterio es funcional (que mutpb suba y baje).
- [PENDIENTE: valores congelados de CFG y LAMBDA, con su justificación]: Resuelto en las Fases 3 y 4.
- [PENDIENTE: esfuerzo de calibración equivalente para la estática]: Resuelto en la Fase 3: 27 configuraciones × 20 semillas para cada variante

**Evaluación conceptual del mecanismo adaptativo (atributo 3)**
- Fortaleza: reacciona a la pérdida de diversidad sin intervención manual; la diferencia entre variantes queda aislada en un solo mecanismo.
- Debilidad: depende de umbrales (ventana, div_min) que se calibran con pocas semillas.
- Límite: δ es un máximo y da poca señal de gradiente, por lo que la retroalimentación puede no tener efecto sobre esa métrica.
- [PENDIENTE: costo de medir diversidad y sensibilidad a los umbrales, una vez rediseñado el lazo]: Resuelto en la Fase 4: la diversidad se mide con 100 pares muestreados; sensibilidad a los umbrales vista en la rejilla de 27 configuraciones

**Pendientes con el asesor**
- Forma de la señal de δ en el fitness (contar celdas en el máximo, además del máximo).
- Tamaño de muestra: con corridas de unos 2 s, la restricción de cómputo que justificaba n = 30 en el protocolo deja de aplicar; la justificación sería la potencia estadística. Resuelto: n = 100.
- Contraste con sboxU (requiere Sage) y comparación con el estado del arte (heredados de la fase 1).

**Hito:** parámetros congelados en la Fase 4 (ver ahí).

### Fase 2b: correcciones del motor y de las pruebas

**Fecha:** 8 de noviembre, 2026

**Responsables:** Christian Regina Rodríguez Magaña

**Qué se corrigió**
- Revisión de la rama fase-2-motor contra el protocolo. Hallazgos: el AG casi no superaba a la búsqueda aleatoria (fitness ≈ 86 contra 85.8 con el mismo presupuesto); la adaptativa no usaba NL ni δ; mutpb se saturaba cerca del tope; `test_misma_poblacion_inicial` era vacuo; los CSV tenían saltos de línea de Windows.
- NL y δ se calculan una sola vez por individuo (`metricas`, `fitness_de`, `_evaluar`), y se guardan en el individuo. La generación de descendientes se separó en `_descendencia`.
- El CSV registra además fit_max_pob, nl_prom y delta_prom. LAMBDA pasó a `CFG["lam"]`.
- Saltos de línea LF (`.gitattributes`, `lineterminator="\n"`), versiones mínimas en requirements.txt, resultados viejos en resultados/archivo_v1.

**Pruebas** (python -m pytest -q)
- 34 pruebas pasan y 1 se salta (el contraste con sboxU, que usa `importorskip`).
- Nuevas: esquema del CSV, elitismo real (fit_max_pob de la población frente a fit_mejor del Hall of Fame), consistencia de NL, δ y fitness, propiedad de que toda descendencia tiene métricas vigentes, reproducibilidad de la adaptativa, misma población inicial (ahora no vacuo) y población inicial distinta con semillas distintas.
- Regresión dorada: con las mismas semillas, el motor refactorizado produjo CSV idénticos, al número, a los 8 casos viejos (5 estáticas y 2 adaptativas, más una de control).
- Pruebas de mutación manuales: se rompió el código a propósito (sin elitismo, sin invalidar el fitness tras mutar o cruzar, la adaptativa modificando cxpb) y los tests fallan. Dos tests de la primera versión no detectaban nada y se rehicieron.

**Supuestos y decisiones**
- sboxU se pospone. La versión 2.x compila con pip pero falla al importar sin SageMath; el paquete `sboxu` de PyPI (1.1.0) es un cascarón vacío, por lo que no va en requirements.txt. El riesgo R1 del protocolo cubre este caso. Resuelto en las Fases 4 y 5: se instaló en Colab con Sage y se verificó (sección 7).

**Hito:** motor estable y verificado, listo para calibrar.

---

### Fase 3: calibración de N, G y de la variante estática

**Fecha:** 8 de noviembre, 2026

**Rama:** fase-3-calibracion

**Responsables:** Christian Regina Rodríguez Magaña

**Revisión:** SIN REVISION

**Atributos del estándar ACM SIGSOFT que cubre:** comparación con un referente (7), supuestos explícitos (8).

**Qué se implementó**
- experimentos/baseline_aleatoria.py: búsqueda aleatoria con el mismo presupuesto N × (G + 1) y la misma población inicial que el AG (referencia de sanidad, no una tercera hipótesis).
- experimentos/calibracion_NG.py: barre (N, G) con 20 semillas preliminares (1 a 20), reanudable.
- experimentos/calibracion_estatica.py: rejilla mutpb ∈ {0.1, 0.2, 0.4} × indpb ∈ {0.01, 0.02, 0.05} × k ∈ {2, 3, 5}, 20 semillas, reanudable, con escritura atómica del CSV.
- Criterios escritos antes de ver resultados. Para N y G: (a) la estática supera a la aleatoria (Mann-Whitney unilateral, p < 0.05) y (b) la búsqueda se estanca (≥ 50 % de las corridas no mejoran en el último 20 % de las generaciones); se elige la más barata. Para la estática: mayor fitness medio final; en empate (menos de 0.3), la más cercana a la configuración base.

**Pruebas:** se agregan 5 de la búsqueda aleatoria y 4 de la rejilla de la estática.

**Resultados: calibración de N y G (20 semillas, fitness final medio)**

| N | G | inicial | estática | aleatoria | p (estática > aleatoria) | estancadas |
|---|---|---|---|---|---|---|
| 100 | 100 | 84.10 | 87.10 | 86.10 | 0.0085 | 90 % |
| 100 | 200 | 84.10 | 87.70 | 86.30 | 0.0011 | 95 % |
| 200 | 200 | 84.20 | 87.50 | 86.30 | 0.0123 | 95 % |

Las tres cumplen (a) y (b). Elegida: **N = 100, G = 100** (la más barata). Con solo 8 semillas la lectura había sido distinta (p = 0.038, 0.15 y 0.28), por lo que se descartó decidir con esa muestra.

**Resultados: rejilla de la estática (27 configuraciones × 20 semillas)**
- Elegida: **mutpb = 0.4, indpb = 0.02, k = 5**, con fitness medio 88.30 (NL 98.5, δ 9.1). La primera de la tabla fue mutpb = 0.4, indpb = 0.01, k = 5 con 88.4; la diferencia entra en el empate.
- Compromiso observado: con k = 5 la diversidad final cae a ~0.03 a 0.05 (convergencia prematura medida); con k = 2 se mantiene en ~0.97, pero el fitness baja a ~86.
- Frente a la búsqueda aleatoria (~86.3 con N = 100, G = 100), la estática calibrada gana alrededor de 2 puntos.

**Tiempos (laptop, varios núcleos):** calibración de N y G (60 tareas) 9.8 min; rejilla de la estática (540 corridas) 15.7 min.

**Supuestos y decisiones**
- LAMBDA = 2.0 queda **fijo** y no se calibra.
- Las semillas preliminares no son evidencia de H1.
- Elegir el máximo de 27 medias sobreestima un poco el valor real; el fitness definitivo se mide con las semillas finales.
- Limitación: el óptimo de la estática quedó en el borde de la rejilla (mutpb y k máximos). No se amplió para no dar más esfuerzo de calibración a una variante que a la otra.

**Hito:** estática calibrada y congelada (N = 100, G = 100, mutpb = 0.4, indpb = 0.02, k = 5).

---

### Fase 4: variante adaptativa, modelo de atacante y análisis estadístico

**Fecha:** 8 de noviembre, 2026

**Responsables:** Christian Regina Rodríguez Magaña

**Revisión:** SIN REVISION

**Atributos del estándar ACM SIGSOFT que cubre:** descripción del artefacto (1), evaluación conceptual (3), indicación de la metodología empírica (5), comparación con alternativas y referentes (6 y 7), supuestos explícitos (8).

**Qué se implementó**
- Regla adaptativa rediseñada (`actualizar_parametros`, función pura). Usa NL y δ por separado: contadores de generaciones sin mejora del mejor NL y del mejor δ de la población (`sin_mejora_nl`, `sin_mejora_delta`), más la diversidad.
- Dos modos con histéresis. **Explotar** (parámetros base de la estática): pasa a explorar si NL y δ llevan ≥ ventana generaciones sin mejorar, o si la diversidad cae por debajo de div_min. **Explorar**: sube mutpb e indpb (factor, hasta sus topes) y baja el torneo a k_explorar; vuelve a explotar cuando la diversidad alcanza div_rec, y ahí el estancamiento se mide desde cero.
- Parámetros adaptados: mutpb, indpb y k. La probabilidad de cruce no se adapta (desviación frente al texto del protocolo, que menciona "cruce y mutación").
- Valores fijados antes de calibrar: k_explorar = 3, mutpb_max = 0.8, indpb_max = 0.1, div_rec = 0.6.
- El CSV de ambas variantes registra ahora nl_max_pob, delta_min_pob, sin_mejora_nl, sin_mejora_delta, indpb y k (la estática repite sus valores fijos).
- src/evaluador.py: `sesgo_lineal` y `prob_diferencial` (modelo de atacante).
- experimentos/calibracion_adaptativa.py: rejilla ventana ∈ {5, 10, 20} × div_min ∈ {0.05, 0.15, 0.30} × factor ∈ {1.25, 1.5, 2.0}, 20 semillas preliminares, con la estática calibrada como referencia (no interviene en la elección).
- analisis/estadistica.py (Módulo 6): Mann-Whitney unilateral con Holm, Wilcoxon pareado, IC 95 % bootstrap pareado, delta de Cliff, medidas secundarias, comparación contra búsqueda aleatoria y AES, análisis del mecanismo y gráficas de convergencia.

**Problema detectado y corregido (primera versión de la regla)**
- Sin histéresis, la adaptativa entraba a "explorar" y no salía nunca (los contadores solo se reinician cuando el mejor mejora, y en exploración casi nunca mejora). Terminaba con mutpb = 0.8 y k = 3 cerca del 80 % del tiempo, comportándose como búsqueda casi aleatoria (fitness 86). La versión final explora ~20 a 43 % del tiempo, con 12 a 14 cambios de modo por corrida.

**Pruebas** (python -m pytest -q)
- La suite completa pasa, con 1 prueba saltada (sboxU). Total al cierre del proyecto: ver Fases 5a y 5b.
- Prueba clave: con factor = 1.0 y k_explorar = k, la adaptativa produce un CSV idéntico al de la estática (salvo la columna `variante`), lo que demuestra que la única diferencia entre variantes es el control de parámetros. Una prueba complementaria verifica que con control activo sí se distinguen.
- La estática no cambió: con el motor nuevo produce CSV idéntico, al número, al del motor anterior.
- Pruebas de mutación manuales (la regla y los contadores) y del análisis estadístico: se rompió el código a propósito (sin histéresis, AND por OR, sin bajar k, sin respetar topes, contadores de NL y de δ al revés, sin reiniciar contadores, sentido de la prueba invertido, Holm mal aplicado, bootstrap no pareado, ventana del mecanismo) y los tests fallan. Dos mutaciones sobrevivían a la primera versión de los tests, se agregaron pruebas y ya se detectan.
- Sesgo lineal verificado contra AES (0.0625) y contra el espectro de Walsh calculado aparte en 5 S-boxes.

**Resultados: calibración de la adaptativa (27 configuraciones × 20 semillas)**
- Compuerta: las 27 son elegibles (exploran entre 20 y 43 % del tiempo, mutpb medio ~0.5 con tope 0.8).
- Elegida: **ventana = 20, div_min = 0.05, factor = 2.0**, con fitness medio 88.40 (NL 98.0, δ 8.8, explora 20 %).
- Referencia (estática calibrada, mismas semillas): 88.30 (NL 98.5, δ 9.1). Diferencia de 0.1, dentro del ruido.
- La mediana de las 27 configuraciones ronda 87.0; solo 2 igualan o superan a la estática. Las mejores configuraciones son las que menos exploran.
- Aviso: ambas variantes se eligieron como el máximo de 27 medias sobre las mismas semillas, por lo que las comparaciones sobre esas semillas están sesgadas hacia arriba y sus valores p no son válidos para H1.

**Resultados exploratorios del mecanismo (semillas de calibración, no es evidencia de H1)**
- Comparación sobre las 20 semillas preliminares: sin diferencias significativas en NL, δ ni fitness. La adaptativa tiene δ medio algo menor (8.8 contra 9.1) y NL algo menor (98.0 contra 98.5); el sesgo lineal y la probabilidad diferencial quedan al mismo nivel.
- Mejora del fitness tras entrar a explorar, contra la estática en las mismas generaciones:

| Ventana | Adaptativa | Estática | Diferencia |
|---|---|---|---|
| 10 generaciones | 0.11 | 0.47 | −0.36 |
| 20 generaciones | 0.49 | 0.75 | −0.26 |
| 30 generaciones | 0.82 | 0.94 | −0.12 |

La exploración parece costar mejora a corto plazo y recuperarse gradualmente, sin que la adaptativa alcance a la estática dentro de 30 generaciones. Es descriptivo (los eventos de una misma corrida no son independientes y la composición de eventos cambia con la ventana).

**Evaluación conceptual del mecanismo adaptativo (atributo 3)**
- Fortaleza: reacciona al resultado de los ataques simulados y a la pérdida de diversidad sin intervención manual; la diferencia entre variantes queda aislada en el lazo de control (probado).
- Debilidad: depende de umbrales calibrados con pocas semillas, y explorar tiene un costo inmediato que a G = 100 no se amortiza.
- Límite: δ tiene poca señal de gradiente (casi no cambia en el mejor individuo), y el fitness toma pocos valores, con muchos empates.

**Supuestos y decisiones**
- Lectura del protocolo (confirmada con el asesor): "adaptarse a ataques" significa usar el resultado de los ataques lineal y diferencial simulados (NL y δ) como señal del lazo. No se implementa un ataque real; el protocolo (1.1.4) excluye diseñar un cifrado completo.
- Los parámetros del lazo (k_explorar, topes, div_rec) se fijaron antes de calibrar; ventana, div_min y factor, con la rejilla anterior.
- No se ajusta más la regla tras ver estos resultados. Si la adaptativa no supera a la estática en las corridas finales, es un resultado válido (riesgo R4) y se discute con el mecanismo de arriba.
- Experimento suplementario: se ejecutó (ver Fase 5).

**Pendientes**
- Escribir en config.py ventana = 20, div_min = 0.05 y factor = 2.0, quitando "PROVISIONAL". Resuelto en la Fase 5: config.py congelado.
- Etapa 5: correr_todo.py (estática, adaptativa y aleatoria, 100 semillas), cifrado.py y contraste de S-boxes. Resuelto en las Fases 5a y 5b.

**Hito:** parámetros congelados en config.py (N = 100, G = 100, mutpb = 0.4, indpb = 0.02, k = 5, λ = 2; ventana = 20, div_min = 0.05, factor = 2.0), etiqueta congelado-v1.

---

### Fase 4b: contraste con sboxU (8 y 9 de noviembre, 2026).

- sboxU 2.0 compilado en Colab con Sage de conda-forge (micromamba, entorno aparte; condacolab falló con HTTP 504 al bajar Miniforge). Se usó el Python del entorno (`python -m pip install --no-build-isolation`), porque el `sage` de conda-forge ya no acepta `-pip` ni `-python`.
- `experimentos/contraste_sboxu.py`: AES + 50 permutaciones aleatorias (semilla 0). Resultado: 51/51 coinciden en (NL, δ) entre `evaluador.py`, `verificacion.py` (FWHT y conteo directo) y sboxU. `tests/test_sboxu.py` pasa (ya no se salta).
- Cierra el riesgo R1. En requirements.txt sboxU sigue sin listarse: solo es instalable con Sage.

---

### Experimento suplementario (exploratorio): horizonte largo

Declarado antes de ejecutarse (12 de noviembre, 2026).
- Pregunta: ¿el costo de explorar de la adaptativa se amortiza con más generaciones?
- Diseño: G = 300 (el resto, igual que las corridas finales: N = 100, parámetros congelados, λ = 2), semillas 1000 a 1039 (n = 40), las tres variantes con las mismas semillas.
- Es exploratorio: no reemplaza la prueba de H1 (G = 100, n = 100), que ya se reportó. Se reporta cualquiera sea el resultado. No se recalibran parámetros.
- Motivo: en las corridas finales la adaptativa no superó a la estática; el mecanismo sugiere que explorar cuesta a corto plazo.
- Registro: el diseño se acordó y escribió antes de ejecutar (12 de noviembre de 2026); `meta.json` marca el inicio de la corrida a las 13:00:31 de ese día.

---

### Fase 5a: corridas finales y análisis (prueba de H1)

**Fecha:** 12 de noviembre, 2026

**Rama:** fase-5-corridas-finales

**Responsables:** Christian Regina Rodríguez Magaña

**Revisión:** SIN REVISION

**Versión del código:** etiqueta `congelado-v1` (commit 6334e2f, el que registra `meta.json` de las corridas finales)

**Qué se implementó**
- `experimentos/correr_todo.py`: corre estática, adaptativa y aleatoria con las semillas 1000 a 1099 (300 corridas). Reanudable, con escritura atómica de cada CSV, guarda la mejor S-box de cada corrida del AG (`sboxes/*.json`), `meta.json` (configuración, commit, fecha) y `entorno.txt`. Se niega a correr si `config.py` no coincide con la configuración congelada o si el directorio contiene corridas de otra configuración.
- `src/cifrado.py`: sustitución byte a byte con una S-box, con su inversa y variantes para archivos. Pruebas de ida y vuelta con SHA-256 sobre texto, datos vacíos y un binario aleatorio de 3 MB. Se aplicó a archivos reales con las S-boxes generadas por el AG en la Fase 5b. Es un esquema de demostración, no un cifrado seguro.
- `experimentos/contraste_final.py`: recalcula NL, δ y fitness de las S-boxes finales con el evaluador, con `verificacion.py` y con sboxU, y los compara con lo guardado en cada corrida.
- Pruebas de `correr_todo`, `cifrado` y `contraste_final`, con pruebas de mutación manuales (corridas no repetidas, configuraciones no mezcladas, la adaptativa corre como adaptativa, cada implementación del contraste cuenta). Suite: 103 pruebas pasan y 1 se salta (sboxU) en el Python de Colab; con sboxU en el entorno de Sage, 104 pasan sin saltos.

**Resultados (n = 100 por variante, semillas 1000 a 1099 en las tres; media y desviación estándar)**

| Variante | NL | δ | Fitness | Sesgo lineal | Prob. diferencial |
|---|---|---|---|---|---|
| Estática | 98.58 (0.96) | 9.44 (0.90) | 87.70 (1.69) | 0.1149 | 0.0369 |
| Adaptativa | 98.16 (0.73) | 9.34 (0.95) | 87.48 (1.83) | 0.1166 | 0.0365 |
| Aleatoria | 97.82 (0.64) | 9.84 (0.55) | 86.14 (0.51) | 0.1179 | 0.0384 |
| AES (cota) | 112 | 4 | 112 | 0.0625 | 0.0156 |

**Prueba de H1: adaptativa contra estática** (diferencia adaptativa − estática, IC 95 % por bootstrap pareado, Mann-Whitney unilateral con corrección de Holm)

| Métrica | Sentido | Diferencia | IC 95 % | p (Holm) | Cliff |
|---|---|---|---|---|---|
| NL | mayor | −0.42 | [−0.64, −0.20] | 1.000 | −0.20 |
| δ | menor | −0.10 | [−0.30, 0.08] | 0.667 | 0.05 |
| Fitness | mayor | −0.22 | [−0.56, 0.12] | 1.000 | −0.09 |

La sensibilidad con Wilcoxon pareado da las mismas conclusiones (p = 0.9998, 0.159, 0.850 sin corregir).

**Conclusión sobre H1:** no se encuentra evidencia de que la variante adaptativa supere a la estática en NL, δ ni fitness. Se mantiene la hipótesis nula. La cota superior del IC del fitness (+0.12, aproximadamente 0.07 desviaciones estándar) descarta una mejora relevante de la adaptativa con este diseño. En NL la adaptativa es algo menor, y el IC excluye el cero; por ser pruebas unilaterales se reporta como descriptivo.

**Comparación con la búsqueda aleatoria (referente de sanidad, atributo 7 del estándar)**
- Estática: +1.56 de fitness [1.22, 1.90], Cliff 0.52, p < 0.001 (Holm).
- Adaptativa: +1.34 [0.96, 1.72], Cliff 0.38, p < 0.001 (Holm).
- Ambas superan a la aleatoria con el mismo presupuesto de evaluaciones. Ninguna se acerca a AES: el mejor NL obtenido fue 100 (AES 112) y el mejor δ, 8 (AES 4). El sesgo del mejor ataque lineal es ≈ 1.8 veces el de AES y la probabilidad del mejor ataque diferencial ≈ 2.4 veces.

**Medidas secundarias (descriptivas)**
- AUC del fitness a lo largo de las generaciones: diferencia −0.09 [−0.24, 0.07].
- NL medio de la población final: adaptativa 94.84 contra estática 97.46 (−2.62 [−2.91, −2.33]). δ medio final: 10.54 contra 9.82. La adaptativa conserva una población más diversa y menos convergida; esto no se traduce en mejores mejores individuos.

**Mecanismo (descriptivo)**: en 387 eventos de entrada a modo explorar, el fitness mejora en promedio 0.057 en las 10 generaciones siguientes en la adaptativa contra 0.098 que mejora la estática en esas mismas generaciones. Explorar tiene un costo a corto plazo que no se recupera dentro de ese horizonte. Los eventos de una misma corrida no son independientes, por lo que no se reportan pruebas.

**Verificaciones**
- Contraste de las S-boxes finales (`contraste_final.py`, Colab, entorno de Sage con sboxU 2.0): 200/200 S-boxes coinciden en NL, δ y fitness entre `evaluador.py`, `verificacion.py` y sboxU. `contraste_sboxu.py`: 51/51. `tests/test_sboxu.py` pasa.
- Reproducibilidad del análisis: al volver a ejecutar `analisis/estadistica.py` sobre los CSV del repositorio se obtienen las mismas tablas que en la laptop.
- Reproducibilidad entre máquinas: 3 semillas (1000 a 1002) × 3 variantes recalculadas en Colab con la configuración congelada (CSV de las tres variantes y S-boxes de estática y adaptativa): 15/15 archivos idénticos byte a byte a `resultados/final` (laptop, Python 3.14.7; Colab, entorno de Sage con Python 3.14.10, commit b27f11f). Evidencia en `evidencia/colab_2026-11-14/`. No se probó con otra versión mayor de Python.
- `demo_cifrado.py`: con una S-box final (estática, semilla 1000; NL = 100, δ = 10) cifra y descifra un mensaje corto, con SHA-256 idéntico al original. Es solo un ejemplo ilustrativo; el cifrado de archivos con las mejores S-boxes está en la Fase 5b.

**Supuestos y limitaciones**
- Los parámetros de ambas variantes se calibraron con 27 configuraciones × 20 semillas preliminares y se congelaron antes de estas corridas. El óptimo de ambas rejillas quedó en el borde.
- El atacante es simulado mediante NL y δ (Lectura A); no se implementa un ataque criptoanalítico.
- El fitness toma pocos valores distintos, con muchos empates.
- Con n = 100 el diseño detecta efectos de d ≈ 0.36 (unilateral) con 80 % de potencia.
- Trazabilidad: `meta.json` de las corridas finales registra el commit 6334e2f (etiqueta congelado-v1). El modo `--suplementario` de `correr_todo.py` y `contraste_final.py` se agregaron después de ese commit; el motor (`src/`) y `config.py` no cambiaron. El `meta.json` del experimento suplementario también dice 6334e2f porque se ejecutó con esos cambios aún sin confirmar; su configuración (G = 300) está en el propio archivo.

### Experimento suplementario (exploratorio): horizonte largo, G = 300

**Declarado antes de ejecutarse** (ver sección anterior). Diseño: G = 300, resto de la configuración congelada, semillas 1000 a 1039 (n = 40), las tres variantes. No reemplaza la prueba de H1 ni se recalibró nada.

**Verificación de coherencia:** en las 40 semillas y las tres variantes, las primeras 100 generaciones de las corridas de G = 300 son idénticas a las de las corridas finales. Los promedios de G = 100 en estas 40 semillas (87.70, 87.50, 86.15) coinciden con los de las 100 semillas, por lo que la submuestra es representativa.

**Resultados (fitness final, media)**

| Variante | G = 100 (mismas 40 semillas) | G = 300 |
|---|---|---|
| Estática | 87.70 | 88.70 |
| Adaptativa | 87.50 | 88.75 |
| Aleatoria | 86.15 | 86.20 |

Adaptativa − estática en G = 300: fitness +0.05 [−0.70, 0.80]; δ −0.25 [−0.60, 0.10] (p = 0.13 sin corregir, 0.40 con Holm); NL −0.45 [−0.85, −0.05]. Ambas superan a la aleatoria por ≈ 2.5 puntos (p < 0.001). Mecanismo: 604 eventos, mejora posterior de 0.020 (adaptativa) contra 0.066 (estática). NL medio de la población final: 94.71 contra 97.91.

**Lectura:** con más generaciones la diferencia de fitness entre variantes pasa de −0.22 a +0.05, en la dirección de la hipótesis de que el costo de explorar se amortiza con un horizonte mayor, pero el intervalo, con n = 40, incluye tanto una pequeña ventaja como una pequeña desventaja. No hay evidencia para afirmar que la adaptativa supera a la estática a G = 300. En las mismas 40 semillas, pasar de G = 100 a G = 300 aporta +1.00 de fitness a la estática, +1.25 a la adaptativa y +0.05 a la aleatoria. Se presenta como pista para trabajo futuro (un horizonte más largo con más semillas, declarado de antemano), no como hallazgo. Con n = 40 los valores p son exploratorios.

### Discusión (borrador)
- La hipótesis H1 no se sostiene con el diseño final. El resultado es válido y está previsto en el protocolo (riesgo R4).
- Explicaciones posibles, a tratar como hipótesis y no como hechos probados: (1) explorar tiene un costo inmediato (mecanismo) que a G = 100 no se amortiza; (2) δ casi no cambia en el mejor individuo, por lo que la señal de estancamiento de δ aporta poco al lazo; (3) el fitness toma pocos valores, con muchos empates; (4) la estática calibrada ya es un baseline fuerte; (5) calibrar ambas con 20 semillas pudo sobreestimar a ambas.
- La contribución verificable: el AG supera a la búsqueda aleatoria; la diferencia entre variantes queda aislada en el lazo de control (prueba de identidad con control neutro); el experimento está acotado, es reproducible y se reporta completo.

**Hito de la Fase 5a:** corridas finales completas (300) y verificadas con sboxU (200/200); H1 no se sostiene; experimento suplementario ejecutado.

---

### Fase 5b: cifrado de archivos binarios con las S-boxes generadas

**Fecha:** 15 de noviembre, 2026

**Rama:** fase-5b-cifrado

**Responsables:** Christian Regina Rodríguez Magaña

**Revisión:** SIN REVISION

**Qué se implementó**
- `experimentos/generar_muestras.py`: genera de forma determinista los archivos de ejemplo (`ejemplos/`): texto en español con acentos y símbolos (769 B), PNG de 256×256 (3222 B), ejecutable ELF x86-64 mínimo de 129 B que solo termina con código 0, y un archivo vacío. Además, cada corrida genera 1 MiB de bytes aleatorios (semilla fija, no se guarda en el repo).
- `experimentos/cifrar_archivos.py`: toma la mejor S-box de cada variante y AES como referencia, cifra y descifra cada archivo con `src/cifrado.py`, y escribe `resultados/cifrado/cifrado_archivos.csv` y `comparacion_sboxes.csv`. Sale con error si alguna combinación falla.
- Regla de "mejor S-box", fijada antes de ver resultados: mayor fitness; en empate, menor δ; en empate, menor semilla.

**Qué se comprueba por cada combinación (3 S-boxes × 5 archivos = 15)**
- El SHA-256 del archivo recuperado es igual al del original.
- El archivo cifrado es distinto del original (no aplica al archivo vacío).
- El ejecutable recuperado se ejecuta y termina con código 0 (solo en Linux; en otros sistemas queda como n/a).

**Resultados**

| S-box | Semilla | NL | δ | Fitness | Sesgo lineal | Prob. diferencial |
|---|---|---|---|---|---|---|
| Mejor estática | 1008 | 100 | 8 | 92.0 | 0.1094 | 0.0312 |
| Mejor adaptativa | 1036 | 100 | 8 | 92.0 | 0.1094 | 0.0312 |
| AES | – | 112 | 4 | 112.0 | 0.0625 | 0.0156 |

- 15/15 combinaciones recuperan el archivo idéntico, con las tres S-boxes.
- Las dos mejores S-boxes empatan en NL, δ y fitness; la regla de desempate solo sirvió para elegir dentro de cada variante.

**Pruebas** (python -m pytest -q)
- 16 pruebas nuevas (`tests/test_cifrar_archivos.py`). Suite completa: 119 pasan y 1 se salta (sboxU).
- Cubren: muestras deterministas y válidas (firma PNG, ELF), la regla de la mejor S-box con empates, que no mezcla variantes, el recálculo de métricas de AES (112 y 4) y de λ = 2, la ejecución completa, y que se detectan un descifrado corrupto, un cifrado que no cambia nada, un hash que no coincide y un ejecutable que no corre.
- Pruebas de mutación manuales: se rompió el código a propósito (criterio de mejor invertido en fitness, δ y semilla; comparación de hash siempre verdadera; cifrado distinto siempre verdadero; archivo vacío sin tratamiento aparte; ejecución que ignora el código de salida; fallos que ignoran el hash o la ejecución; λ distinto). Cinco mutaciones sobrevivían a la primera versión de las pruebas y se agregaron pruebas para detectarlas.

**Supuestos y limitaciones**
- Es un esquema demostrativo. Cada byte se sustituye siempre por el mismo byte (sustitución monoalfabética), por lo que conserva la estructura de frecuencias del archivo y no es seguro por sí solo. Demuestra que las S-boxes obtenidas son biyectivas, reversibles y utilizables como componente de sustitución, no que protejan datos.
- Las "mejores" S-boxes son el máximo de 100 corridas, no una S-box típica. El rendimiento esperado de cada variante es el de la tabla de la Fase 5a (fitness medio 87.70 y 87.48).
- La comparación con AES es solo de métricas (NL y δ); no se evalúa su resistencia a ataques reales.
- La ejecución del archivo recuperado solo se comprueba en Linux.

**Cómo reproducir:** `python -m experimentos.generar_muestras` y luego `python -m experimentos.cifrar_archivos`.

**Hito:** las S-boxes generadas por el AG funcionan como componente de sustitución reversible sobre archivos binarios reales; queda cerrada la implementación y falta el análisis final y la documentación (Fase 6).

---

## 9. Referencias principales

- Hevner, A. R., March, S. T., Park, J., y Ram, S. (2004). Design science in information systems research. MIS Quarterly, 28(1), 75-105.
- Peffers, K., Tuunanen, T., Rothenberger, M. A., y Chatterjee, S. (2007). A design science research methodology for information systems research. Journal of Management Information Systems, 24(3), 45-77.
- Daemen, J., y Rijmen, V. (2002). The design of Rijndael: AES, the Advanced Encryption Standard. Springer.
- Lista completa en el protocolo de investigación.