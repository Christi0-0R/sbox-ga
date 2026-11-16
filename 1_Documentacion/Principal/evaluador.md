# src/evaluador.py (Módulo 2: evaluador criptográfico)

**Para qué existe:** calificar cualquier S-box. El AG lo llama una vez por cada individuo nuevo (≈ 10,000 veces por corrida), por eso está vectorizado con NumPy.

## Funciones

| Función | Entrada → salida | Cómo |
|---|---|---|
| `es_permutacion(sbox)` | lista → bool | Comprueba que contenga 0 … 255 sin repetir. |
| `ddt(sbox)` | → matriz 256×256 | `T[dx, dy]` = número de x con `S(x) ⊕ S(x ⊕ dx) = dy`. Se arma toda la matriz `S(x) ⊕ S(x ⊕ dx)` de una vez y se cuenta con `np.bincount`. |
| `delta(sbox)` | → int | Máximo de la DDT sin la fila `dx = 0` (que siempre vale 256 en `dy = 0`). |
| `walsh(sbox)` | → matriz 256×256 | Espectro `W[a, b] = Σₓ (−1)^(a·x ⊕ b·S(x))`, calculado como producto de la matriz de Hadamard `H[a, x]` por `F[x, b]`. La LAT es `W / 2`. |
| `nl(sbox)` | → int | `128 − max|W[a, b]| / 2` con `b ≠ 0` (la columna `b = 0` no es una función componente). |
| `metricas(sbox)` | → (NL, δ) | Calcula ambas una sola vez; es la que usa el motor. |
| `fitness_de(nl, δ, lam)` | → float | `NL − lam·(δ − 4)`. Con `lam = 2`, AES da 112. |
| `fitness(sbox, lam)` | → float | Atajo: `fitness_de(*metricas(sbox))`. |
| `sesgo_lineal(nl)` | → float | Sesgo del mejor ataque lineal: `(128 − NL) / 256`. AES: 0.0625. |
| `prob_diferencial(δ)` | → float | Probabilidad del mejor ataque diferencial: `δ / 256`. AES: 0.0156. |

## Por qué el fitness es `NL − 2(δ − 4)`

- Es mono-objetivo y agregado (decisión metodológica del protocolo, sección 2.2).
- Restar 4 hace que AES quede como cota natural (fitness = NL = 112 cuando δ = 4).
- `lam = 2` está **fijo** desde antes de calibrar (riesgo R7). Con eso, bajar δ en 2 vale lo mismo que subir NL en 4. Como NL y δ casi siempre son pares, el fitness toma pocos valores distintos (muchos empates en las pruebas estadísticas).

## Modelo de atacante

NL y δ son, respectivamente, la fuerza del mejor ataque lineal y del mejor ataque diferencial contra la S-box sola. `sesgo_lineal` y `prob_diferencial` los expresan en la escala del atacante. La variante adaptativa reacciona al estancamiento de estas dos señales; la estática no. No se implementa un ataque criptoanalítico real.

## Cómo se verifica (`tests/test_evaluador.py`)

- Regresión: AES da NL = 112, δ = 4, fitness = 112, sesgo 0.0625, probabilidad 0.0156.
- La identidad (x → x) es lineal: NL = 0, δ = 256.
- Cada fila de la DDT suma 256.
- Coincide con `verificacion.py` en AES y en permutaciones aleatorias.
- `sesgo_lineal` coincide con el máximo del espectro de Walsh calculado aparte.
