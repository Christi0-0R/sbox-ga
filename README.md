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
| Extendida (adaptativa) | El mismo AG con un lazo que ajusta parámetros según diversidad, estancamiento y evolución de NL y δ | Contribución propuesta |

La única diferencia entre versiones es el lazo de control de parámetros. DEAP, NumPy y el evaluador criptográfico son componentes de apoyo, no la contribución.

### 2.2 Método de evaluación empírica

Se usa una **simulación cuantitativa** (tipo iv del estándar ACM SIGSOFT): el artefacto se evalúa en un entorno computacional artificial frente a un artefacto competidor, la versión estática.

- 30 ejecuciones independientes por variante, con las mismas 30 semillas para ambas.
- Mismos función de fitness, tamaño de población (N) y número de generaciones (G).
- Prueba U de Mann-Whitney sobre NL, δ y fitness final de cada corrida.
- Referencia adicional: la S-box de AES (NL = 112, δ = 4) como cota de comparación.

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

## 4. Supuestos explícitos

1. La S-box de AES es una cota de referencia (NL = 112, δ = 4), no un objetivo a superar.
2. El fitness es mono-objetivo y agregado: NL menos LAMBDA por (δ - 4). Es una decisión metodológica, no una afirmación de que sea la mejor forma de combinar ambas métricas.
3. N = 30 y G = 50 se mantienen iguales en ambas variantes.
4. Los pesos del fitness y los umbrales de la variante adaptativa son **provisionales**. Se calibran con corridas preliminares y se congelan antes de las 60 corridas finales. No se modifican después de ver sus resultados.
5. Las corridas preliminares usan semillas distintas a las finales (las finales son 1000 a 1029).
6. Con n = 30 por variante, el diseño detecta con 80 % de potencia efectos grandes (d ≈ 0.74 o mayor). Diferencias pequeñas o medianas podrían no detectarse.

## 5. Estructura del repositorio

```
sbox-ga/
├── README.md
├── requirements.txt
├── src/
│   ├── gf256.py          # Módulo 1: álgebra de GF(2^8) y S-box de AES
│   ├── evaluador.py      # Módulo 2: DDT, LAT/Walsh, NL, delta, fitness
│   ├── motor_ga.py       # Módulo 3: AG estático y adaptativo
│   ├── verificacion.py   # Módulo 4: regresión y contraste
│   └── cifrado.py        # Módulo 5: cifrado de archivos binarios
├── tests/                # pruebas automáticas (pytest)
├── experimentos/
│   ├── config.py         # parámetros compartidos por ambas variantes
│   └── correr_todo.py    # lanza las 60 corridas
├── resultados/           # un CSV por corrida (no se editan a mano)
├── analisis/
│   └── estadistica.py    # Módulo 6: Mann-Whitney, tablas y gráficas
└── notebooks/
    └── colab_main.ipynb  # clona el repo y ejecuta en Google Colab
```

## 6. Entorno

- **Laptop (desarrollo):** Python 3.14, entorno virtual `.venv`.
- **Google Colab (experimentos):** Python, salida de `!python --version.
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
- [X] Fase 1: álgebra de GF(2^8) y evaluador, con regresión contra AES (NL = 112, δ = 4)
- [X] Fase 2: motor evolutivo (estático, corridas preliminares, adaptativo)
- [ ] Fase 3: 60 corridas y verificación cruzada
- [ ] Fase 4: análisis estadístico, cifrado de archivos y comparación con AES
- [ ] Fase 5: documento final

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

---

## 9. Referencias principales

- Hevner, A. R., March, S. T., Park, J., y Ram, S. (2004). Design science in information systems research. MIS Quarterly, 28(1), 75-105.
- Peffers, K., Tuunanen, T., Rothenberger, M. A., y Chatterjee, S. (2007). A design science research methodology for information systems research. Journal of Management Information Systems, 24(3), 45-77.
- Daemen, J., y Rijmen, V. (2002). The design of Rijndael: AES, the Advanced Encryption Standard. Springer.
- Lista completa en el protocolo de investigación.