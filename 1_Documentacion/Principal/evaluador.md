# evaluador.py (El juez criptografico)

Dada una s-box (lista de 256 valores), calcula DDT, espectro de Walsh, NL, δ y fitness. Es lo que el AG llama miles de veces, por eso esta vectorizado con NumpyPy.

**Constantes precalculadas (se hacen una sola vez al importar)**

- `_X = np.arange(256)`: vector 0..255
- `_PAR`: tabla de paridad; `_PAR[i]` = 1 si `i` tiene cantidad impar de unos, 0 si par. Sirve para calcular el producto punto binario `ax` (que es la paridadde `a & x`)
- `_H`: matriz de Hadamard 256x256 con `H[a, x] = (-1)^(ax)`. `np.bitwise_and.outer(_X, _X)` hace `a & x` para todas las parejas; se calcula la paridad y se convierte a ±1 con `1 - 2*paridad` 
- `_FILAS = (arange(256)*256)[:, None]`: offsets por fila, un truco para el `bincount` de la DDT (abajo)

## Funciones

`es_permutacion(sbox)`: Ordena los valores y verifica que sean exactamente 0..255. Es el chequeo de biyectividad.

**`ddt(sbox)`: tabla de distribución de diferencias -** `T[dx, dy]` = cuántos `x` cumplen `S(x) ⊕ S(x⊕dx) = dy`

- `s[_X[None,:] ^ _X[:,None]]`: calcula S(x ⊕ dx) para todas las parejas (dx, x) de golpe, gracias al broadcasting
- `dy = s[None,:] ^ ...`: le hace XOR con `S(x)`. Queda una matriz `dy[dx, x]`
- Luego hay que contar, por cada fila `dx`, cuántas veces aparece cada `dy`. El truco: sumar `_FILAS` (dx·256) a cada `dy` convierte cada pareja (dx, dy) en un índice único de 0..65535, y un solo `np.bincount` cuenta todo. `reshape(256,256)` lo regresa a tabla
- Propiedad que pruebas: cada fila suma 256.

**`delta(sbox)`: uniformidad diferencial -** `ddt(sbox)[1:].max()`: el máximo de la DDT excluyendo la fila 0 `(dx = 0)`, porque ahí siempre vale 256 (diferencia de entrada cero da diferencia de salida cero). Menor δ = mejor resistencia diferencial. AES: 4

**`walsh(sbox)`: espectro de Walsh -** `W[a,b] = Σₓ (-1)^(a·x ⊕ b·S(x))`

- `F[x,b] = (-1)^(b·S(x))`: construye la matriz de las funciones componente
- `_H @ F`: una multiplicación matricial calcula la suma para todos los (a, b) a la vez
- `np.rint(...).astype(int64)`: redondea (los floats pueden traer error de 1e-13) a enteros exactos

**`nl(sbox)`: no-linealidad -** `128 − max|W(a,b)| / 2`, con `b ≠ 0` (por eso `W[:, 1:]`; b=0 sería la función constante). Intuición: mientras más grande sea el sesgo lineal máximo, más cerca está la S-box de una función afín y menor NL. AES: 112

`LAMBDA = 2.0`: Peso con que δ penaliza (Provisional)

`fitness(sbox, lam)`: `NL − λ·(δ − 4)`. Un δ de 4 no penaliza nada (es el de AES); cada unidad extra de δ resta 2 puntos. Con resultados preliminares (NL = 98, δ = 10): 98 − 2·6 = 86.0