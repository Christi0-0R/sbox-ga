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

- **Enfoque:** Ciencia del Diseño (Design Science Research), modelo DSRM de Peffers et al. (2007).
- **Artefacto:** modelo (March y Smith, 1995) de evolución de S-boxes como optimización sobre permutaciones, con fitness mono-objetivo (NL y δ) y lazo de retroalimentación adaptativa.
- **Método de evaluación empírica:** experimento computacional cuantitativo (simulación) que compara dos condiciones, estática vs. adaptativa, con 30 ejecuciones independientes por variante y prueba U de Mann-Whitney.
- **Estándar de referencia:** ACM SIGSOFT Empirical Standards, "Engineering Research (Design Science)".

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

## 7. Nota sobre sboxU

El protocolo contempla sboxU solo como contraste independiente de NL y δ. La versión 2.0 (instalada desde GitHub) requiere SageMath, por lo que **no está incluida en `requirements.txt`**. El evaluador propio (`src/evaluador.py`) es el principal. La forma del contraste del Módulo 4 (Sage en un entorno aparte o una segunda implementación independiente) está pendiente de definir con el asesor.

---

## 8. Estado del proyecto

- [x] Fase 0: repositorio, entorno local, entorno de Colab y pruebas funcionando
- [ ] Fase 1: álgebra de GF(2^8) y evaluador, con regresión contra AES (NL = 112, δ = 4)
- [ ] Fase 2: motor evolutivo (estático, corridas preliminares, adaptativo)
- [ ] Fase 3: 60 corridas y verificación cruzada
- [ ] Fase 4: análisis estadístico, cifrado de archivos y comparación con AES
- [ ] Fase 5: documento final

## 9. Referencias principales

- Hevner, A. R., March, S. T., Park, J., y Ram, S. (2004). Design science in information systems research. MIS Quarterly, 28(1), 75-105.
- Peffers, K., Tuunanen, T., Rothenberger, M. A., y Chatterjee, S. (2007). A design science research methodology for information systems research. Journal of Management Information Systems, 24(3), 45-77.
- Daemen, J., y Rijmen, V. (2002). The design of Rijndael: AES, the Advanced Encryption Standard. Springer.
- Lista completa en el protocolo de investigación.