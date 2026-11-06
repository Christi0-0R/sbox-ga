# verificacion.py (contraste independiente)

Recalcula NL y δ con algoritmos distintos para detectar errores del evaluador (mientras no tenga sboxU)

### delta_directo(sbox)

Python puro, tres ciclos: para cada dx de 1 a 255, cuenta en una lista cuántas veces sale cada diferencia de salida, y se queda con el máximo global. Es la definición literal de δ, lenta pero obviamente correcta.

### _fwht(v): transformada rápida de Walsh-Hadamard

Algoritmo tipo mariposa: en cada nivel h = 1, 2, 4, ... combina pares (a, b) → (a+b, a−b). Calcula en O(n log n) lo que el evaluador hace con una matriz O(n²). Sin normalizar.

### nl_fwht(sbox)

Para cada máscara de salida b = 1..255, construye la función componente f(x) = (-1)^(b·S(x)) (paridad de S(x) & b), le aplica la FWHT, y toma el máximo valor absoluto. NL = 128 − max//2.
