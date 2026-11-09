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
- Mismos función de fitness, tamaño de población (N = 100) y número de generaciones (G = 100).
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
│
├── src/
│   ├── gf256.py                  # Módulo 1: álgebra de GF(2^8) y S-box AES
│   ├── evaluador.py              # Módulo 2: DDT, LAT/Walsh, NL, delta,
│   │                             #         sesgo_lineal, prob_diferencial y fitness
│   ├── motor_ga.py               # Módulo 3: AG estático y adaptativo
│   ├── verificacion.py           # Módulo 4: regresión y contraste
│   └── cifrado.py                # Módulo 5: cifrado de archivos binarios
│
├── tests/                        # Pruebas automáticas (pytest)
│
├── experimentos/
│   ├── config.py                 # Parámetros compartidos por ambas variantes
│   ├── correr_todo.py            # Ejecución de las 60 corridas
│   ├── baseline_aleatoria.py     # Búsqueda aleatoria con el mismo presupuesto
│   ├── calibracion_NG.py         # Fase 3: (N, G) vs. búsqueda aleatoria
│   ├── calibracion_estatica.py   # Fase 3: rejilla de la estática (27 configuraciones)
│   └── calibracion_adaptativa.py # Fase 4: rejilla de la adaptativa (27 configuraciones)
│
├── resultados/
│   ├── archivo_v1/               # Corridas del motor anterior (historial)
│   ├── calib_NG/                 # Resultados de calibración de N y G
│   ├── calib_estatica/           # Resultados de calibración estática
│   └── calib_adaptativa/         # Resultados de calibración adaptativa
│
├── analisis/
│   └── estadistica.py            # Módulo 6: Mann-Whitney, tablas y gráficas
│
└── notebooks/
    └── colab_main.ipynb          # Clona el repositorio y ejecuta en Google Colab
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

El notebook `notebooks/colab_main.ipynb` monta Google Drive, clona este repositorio, instala las dependencias y ejecuta los scripts. Los CSV se escriben a Drive para poder reanudar si la sesión se desconecta.

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

## 7. Verificación cruzada (Módulo 4)

El protocolo contempla sboxU como contraste independiente de NL y δ. La versión 2.0 (instalada desde GitHub) requiere SageMath, por lo que no está incluida en requirements.txt y su uso sigue pendiente de definir con el asesor.

Mientras tanto, src/verificacion.py contiene una segunda implementación escrita con algoritmos distintos a los del evaluador:

| Métrica | Evaluador (src/evaluador.py) | Contraste (src/verificacion.py) |
|---|---|---|
| δ | DDT vectorizada con NumPy | Conteo directo de pares en Python puro |
| NL | Espectro de Walsh por multiplicación matricial | Transformada rápida de Walsh-Hadamard por función componente |

Limitación: ambas implementaciones las escribió el mismo equipo, por lo que es menos independiente que una herramienta externa. Por eso sboxU sigue siendo deseable si se logra instalar.

---

## 8. Estado del proyecto

- [x] Fase 0: repositorio, entorno local, entorno de Colab y pruebas funcionando
- [x] Fase 1: álgebra de GF(2^8) y evaluador, con regresión contra AES (NL = 112, δ = 4)
- [x] Fase 2: motor evolutivo (estático, corridas preliminares, adaptativo inicial)
- [x] Fase 2b: correcciones del motor y de las pruebas
- [x] Fase 3: calibración de N, G y de la estática (compuerta contra búsqueda aleatoria)
- [x] Fase 4: adaptativa rediseñada, modelo de atacante, calibración y Módulo 6
- [ ] Fase 5: corridas finales, cifrado de archivos y contraste de S-boxes
- [ ] Fase 6: análisis de resultados y documento final

## 8.1 Bitácora de fases

### Fase 1: álgebra de GF(2^8) y evaluador

**Fecha:** 31 de octubre, 2026

**Rama / PR:** fase-1-gf256-evaluador / Sin PR (pendiente de merge)

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
- LAMBDA = 2.0 es provisional. Se calibra en las corridas preliminares y se congela antes de las 60 corridas finales (riesgo R7).
- La DDT 4x4 usa la S-box de PRESENT (Bogdanov et al., 2007). [PENDIENTE: contrastar los valores de analisis/ejemplo_4x4.py con la tabla del artículo.]

**Hito:** regresión con AES aprobada, por lo que se puede avanzar a la Fase 2.

**Pendientes heredados**
- Definir con el asesor cómo se hará el contraste con sboxU (requiere Sage).
- Agregar como referencia valores de NL y δ reportados en la literatura (Picek et al., 2016; Clark et al., 2004), extraídos directamente de los artículos.

---

### Fase 2: motor evolutivo

**Fecha:** 5 de noviembre, 2026

**Rama / PR:** fase-2-motor / Sin PR (pendiente de merge)

**Responsables:** Christian Regina Rodríguez Magaña

**Revisión:** SIN REVISION

**Atributos del estándar ACM SIGSOFT que cubre:** descripción del artefacto (1), supuestos explícitos (8), evaluación conceptual (3, pendiente).

**Qué se implementó**
- experimentos/config.py: parámetros compartidos (N = 30, G = 50, cxpb, mutpb, indpb, k, parámetros del lazo adaptativo), semillas finales (1000 a 1029) y semillas preliminares (1 a 5).
- src/motor_ga.py: AG de permutación con DEAP (torneo, PMX, mutShuffleIndexes, elitismo). Una sola base de código para ambas variantes; la única diferencia es la llamada a actualizar_parametros.
- La diversidad se estima como distancia de Hamming media normalizada sobre 100 pares muestreados, con un generador aleatorio independiente para no alterar la secuencia de la evolución.
- experimentos/prelim_estatica.py, experimentos/calibracion.py, analisis/graficas_prelim.py, analisis/resumen_prelim.py.

**Pruebas** (python -m pytest -q)
- 15 pruebas pasan (10 de la fase 1 y 5 del motor).
- Corrida válida (el mejor es permutación), reproducibilidad (misma semilla, mismo CSV), la adaptativa corre, ambas variantes parten de la misma población inicial, y PMX y mutación preservan la permutación en 300 repeticiones.
- [PENDIENTE: prueba en Colab]

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
- [PENDIENTE: valores congelados de CFG y LAMBDA, con su justificación]
- [PENDIENTE: esfuerzo de calibración equivalente para la estática]

**Evaluación conceptual del mecanismo adaptativo (atributo 3)**
- Fortaleza: reacciona a la pérdida de diversidad sin intervención manual; la diferencia entre variantes queda aislada en un solo mecanismo.
- Debilidad: depende de umbrales (ventana, div_min) que se calibran con pocas semillas.
- Límite: δ es un máximo y da poca señal de gradiente, por lo que la retroalimentación puede no tener efecto sobre esa métrica.
- [PENDIENTE: costo de medir diversidad y sensibilidad a los umbrales, una vez rediseñado el lazo]

**Pendientes con el asesor**
- Forma de la señal de δ en el fitness (contar celdas en el máximo, además del máximo).
- Tamaño de muestra: con corridas de unos 2 s, la restricción de cómputo que justificaba n = 30 en el protocolo deja de aplicar; la justificación sería la potencia estadística.
- Contraste con sboxU (requiere Sage) y comparación con el estado del arte (heredados de la fase 1).

**Hito:** [PENDIENTE: parámetros congelados]

### Fase 2b: correcciones del motor y de las pruebas

**Fecha:** 8 de noviembre, 2026

**Responsables:** Christian Regina Rodríguez Magaña

**Qué se corrigió**
- Revisión de la rama fase-2-motor contra el protocolo. Hallazgos: el AG casi no superaba a la búsqueda aleatoria (fitness ≈ 86 contra 85.8 con el mismo presupuesto); la adaptativa no usaba NL ni δ; mutpb se saturaba cerca del tope; `test_misma_poblacion_inicial` era vacuo; los CSV tenían saltos de línea de Windows.
- NL y δ se calculan una sola vez por individuo (`metricas`, `fitness_de`, `_evaluar`), y se guardan en el individuo. La generación de descendientes se separó en `_descendencia`.
- El CSV registra además fit_max_pob, nl_prom y delta_prom. LAMBDA pasó a `CFG["lam"]`.
- Saltos de línea LF (`.gitattributes`, `lineterminator="\n"`), versiones mínimas en requirements.txt, resultados viejos en resultados/archivo_v1.

**Pruebas** (python -m pytest -q)
- 34 pruebas pasan y 1 se salta (el contraste con sboxU, que usa `importorskip`). [PENDIENTE: confirmar con tu salida]
- Nuevas: esquema del CSV, elitismo real (fit_max_pob de la población frente a fit_mejor del Hall of Fame), consistencia de NL, δ y fitness, propiedad de que toda descendencia tiene métricas vigentes, reproducibilidad de la adaptativa, misma población inicial (ahora no vacuo) y población inicial distinta con semillas distintas.
- Regresión dorada: con las mismas semillas, el motor refactorizado produjo CSV idénticos, al número, a los 8 casos viejos (5 estáticas y 2 adaptativas, más una de control).
- Pruebas de mutación manuales: se rompió el código a propósito (sin elitismo, sin invalidar el fitness tras mutar o cruzar, la adaptativa modificando cxpb) y los tests fallan. Dos tests de la primera versión no detectaban nada y se rehicieron.

**Supuestos y decisiones**
- sboxU se pospone. La versión 2.x compila con pip pero falla al importar sin SageMath; el paquete `sboxu` de PyPI (1.1.0) es un cascarón vacío, por lo que no va en requirements.txt. El riesgo R1 del protocolo cubre este caso. [PENDIENTE: definir con el asesor, o intentar Sage en Colab]

**Hito:** motor estable y verificado, listo para calibrar.

---

### Fase 3: calibración de N, G y de la variante estática

**Fecha:** 8 de noviembre, 2026

**Rama / PR:** fase-3-calibracion / [PENDIENTE: PR]

**Responsables:** Christian Regina Rodríguez Magaña

**Revisión:** SIN REVISION

**Atributos del estándar ACM SIGSOFT que cubre:** comparación con un referente (7), supuestos explícitos (8).

**Qué se implementó**
- experimentos/baseline_aleatoria.py: búsqueda aleatoria con el mismo presupuesto N × (G + 1) y la misma población inicial que el AG (referencia de sanidad, no una tercera hipótesis).
- experimentos/calibracion_NG.py: barre (N, G) con 20 semillas preliminares (1 a 20), reanudable.
- experimentos/calibracion_estatica.py: rejilla mutpb ∈ {0.1, 0.2, 0.4} × indpb ∈ {0.01, 0.02, 0.05} × k ∈ {2, 3, 5}, 20 semillas, reanudable, con escritura atómica del CSV.
- Criterios escritos antes de ver resultados. Para N y G: (a) la estática supera a la aleatoria (Mann-Whitney unilateral, p < 0.05) y (b) la búsqueda se estanca (≥ 50 % de las corridas no mejoran en el último 20 % de las generaciones); se elige la más barata. Para la estática: mayor fitness medio final; en empate (menos de 0.3), la más cercana a la configuración base.

**Pruebas:** se agregan 5 de la búsqueda aleatoria y 4 de la rejilla de la estática. [PENDIENTE: total de tu pytest]

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
- LAMBDA = 2.0 queda **fijo** y no se calibra: cambiarlo después de ver resultados invalidaría la comparación (R7). Decisión tomada por los autores sin consulta con el asesor. [PENDIENTE: confirmar con el asesor]
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
- La suite completa pasa, con 1 prueba saltada (sboxU). [PENDIENTE: número exacto de tu pytest; en la copia de verificación fueron 67 y 1 salto, sin contar las 5 de la búsqueda aleatoria]
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
- Lectura del protocolo: "adaptarse a ataques" significa usar el resultado de los ataques lineal y diferencial simulados (NL y δ) como señal del lazo. No se implementa un ataque real; el protocolo (1.1.4) excluye diseñar un cifrado completo. [PENDIENTE: confirmar con el asesor]
- Los parámetros del lazo (k_explorar, topes, div_rec) se fijaron antes de calibrar; ventana, div_min y factor, con la rejilla anterior.
- No se ajusta más la regla tras ver estos resultados. Si la adaptativa no supera a la estática en las corridas finales, es un resultado válido (riesgo R4) y se discute con el mecanismo de arriba.
- Experimento suplementario previsto, exploratorio y declarado antes de correrlo: un horizonte más largo (por ejemplo G = 300) sobre un subconjunto de semillas finales, para ver si el costo de explorar se amortiza. No sustituye la prueba de H1. [PENDIENTE: decidir si se hace]

**Pendientes**
- Escribir en config.py ventana = 20, div_min = 0.05 y factor = 2.0, quitando "PROVISIONAL".
- Etapa 5: correr_todo.py (estática, adaptativa y aleatoria, 100 semillas), cifrado.py y contraste de S-boxes.
- Actualizar el protocolo: N, G y n (4.4, 5.1.2, 5.2, 5.3, R2, 5.8), el modelo de atacante (1, 1.1.2, 1.1.4, 1.3.1, 2.3.3, 2.3.6, 4.5.3), el plan de análisis (4.6) y el riesgo R8 (el atacante es simulado).

**Hito:** [PENDIENTE: parámetros congelados en config.py]

---

## 9. Referencias principales

- Hevner, A. R., March, S. T., Park, J., y Ram, S. (2004). Design science in information systems research. MIS Quarterly, 28(1), 75-105.
- Peffers, K., Tuunanen, T., Rothenberger, M. A., y Chatterjee, S. (2007). A design science research methodology for information systems research. Journal of Management Information Systems, 24(3), 45-77.
- Daemen, J., y Rijmen, V. (2002). The design of Rijndael: AES, the Advanced Encryption Standard. Springer.
- Lista completa en el protocolo de investigación.