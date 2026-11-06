# Explicacion de la estructura y archivos

## La idea general

- Una S-box es una tabla de 256 números que “revuelve” bytes (cada número del 0 al 255 se cambia por otro, sin repetir). Es la pieza que hace difícil descifrar un mensaje sin la clave.

- Hay dos medidas de qué tan buena es: NL (más alta = mejor) y δ (más baja = mejor). La S-box de AES tiene NL = 112 y δ = 4, y es la referencia.

- Como hay un número absurdo de tablas posibles, no se pueden probar todas. Se usa un algoritmo genético: una población de tablas que “evoluciona” (las mejores se reproducen, se mezclan y mutan). El proyecto compara una versión que no cambia sus reglas con otra que sí las ajusta mientras corre.

## `src/`: las piezas del programa

### `gf256.py`: “la calculadora especial”

- **Qué es**: las matemáticas del campo GF(2⁸), que es un sistema donde sumar y multiplicar números de 0 a 255 siempre da otro número de 0 a 255.

- **Qué hace**: multiplica, saca inversos y, con eso, construye la S-box de AES desde cero.

- **Para qué sirve**: para tener una tabla de la que sabemos la respuesta correcta (NL = 112, δ = 4) y verificar que nuestro “juez” funciona.

- **Analogía**: es como fabricar una regla de 1 metro perfecta para comprobar que tu cinta métrica mide bien.

### `evaluador.py`: “el juez”

- **Qué es**: el programa que califica cualquier S-box.

- **Entra**: una lista de 256 números. Sale: NL, δ y un fitness (una calificación única).

- **Cómo lo hace:**
    - `ddt` y `delta`: cuentan qué tan “predecible” es la tabla (si un cambio en la entrada produce siempre el mismo cambio en la salida, es mala).
    - `walsh` y `nl`: miden qué tan parecida es la tabla a una operación simple y lineal (si se parece mucho, es mala).
    - `fitness`: junta ambas en un número: `NL − 2 × (δ − 4)`.
    - `es_permutacion`: revisa que no haya números repetidos ni faltantes.

- **Analogía**: un juez de concurso que da una calificación final combinando dos criterios.

- **Detalle**: está escrito con NumPy para calificar rápido, porque el algoritmo lo llama miles de veces.

### `verificacion.py`: “el segundo juez”

- **Qué es**: calcula NL y δ otra vez, pero con un método distinto y más lento.

- **Para qué sirve**: si los dos jueces dan siempre lo mismo, es muy probable que ninguno tenga errores.

- **Analogía**: sacar una cuenta con calculadora y luego a mano, para confirmar.

### `motor_ga.py`: “el criadero”

- **Qué es**: el algoritmo genético completo. Es el archivo principal.

- **Qué hace en cada corrida**:
    1. Crea 30 S-boxes al azar (la población inicial).
    2. Las califica con el juez.
    3. Selecciona las mejores (torneo: elige 3 al azar y gana la mejor).
    4. Las cruza (mezcla dos tablas sin repetir números, con PMX).
    5. Las muta (intercambia algunos números de lugar).
    6. Guarda al mejor siempre (elitismo), para no perderlo.
    7. Repite 50 veces y escribe todo en un archivo CSV.

- **Funciones auxiliares**:
    - `diversidad`: mide qué tan distintas son las tablas entre sí (si todas se parecen, la búsqueda se estancó).
    - `actualizar_parametros`: la parte adaptativa. Si la búsqueda se estanca, sube la probabilidad de mutar.

- **Analogía**: un criadero de plantas donde cada generación dejas reproducirse a las mejores. La versión estática siempre usa la misma receta, y la adaptativa cambia la receta si ve que ya no avanza.

## `experimentos/`: los controles y las corridas

### `config.py`: “el panel de perillas”

- **Qué es**: un solo lugar con todos los ajustes (tamaño de población, generaciones, probabilidades de cruce y mutación, etc.) y las listas de semillas.

- **Para qué sirve**: que ambas variantes usen exactamente los mismos ajustes, para que la única diferencia sea la adaptación.

- **Las semillas**: son números que fijan el azar. Con la misma semilla, el programa da siempre el mismo resultado. Se separan en preliminares (1 a 5, para probar) y finales (1000 a 1029, para el experimento real).

### `prelim_estatica.py`: “la prueba de arranque”

- Corre la versión estática con las 5 semillas de prueba y cronometra cada una.

- Sirve para ver si el criadero funciona y dónde se atora.

### `calibracion.py`: “probar las perillas”

- Corre la versión adaptativa con 12 combinaciones de ajustes y 2 controles estáticos, y muestra una línea de resultado por cada una.

- Sirve para decidir qué ajustes usar antes del experimento real. Se hace con semillas de prueba para no “hacer trampa” con las finales.

## `analisis/`: para mirar los resultados

### `ejemplo_4x4.py`: “el ejemplo de juguete”

- Calcula la tabla de diferencias de una S-box diminuta (4 bits, la de PRESENT) para que se vea a ojo lo que el evaluador hace en grande. No forma parte del experimento.

### `graficas_prelim.py`: “los dibujos”

- Lee los CSV y dibuja 4 gráficas (fitness, NL, δ, diversidad contra generación), una línea por semilla. Sirve para ver el estancamiento.

### `resumen_prelim.py`: “los números clave”

- Imprime, para cada semilla, cómo iba en las generaciones 0, 10, 25 y 50. Es la versión en texto de las gráficas.

## `tests/`: las pruebas automáticas

Son programas que revisan que todo lo demás siga funcionando. Se ejecutan con `python -m pytest -q`.

- `test_gf256.py`: comprueba que la calculadora dé resultados conocidos (por ejemplo, que la S-box de AES empiece con 0x63).
- `test_evaluador.py`: comprueba que el juez dé 112 y 4 para AES, que ambos jueces coincidan y que una tabla trivial (x → x) saque la peor nota.
- `test_motor.py`: comprueba que las tablas que produce el criadero sigan siendo válidas, que la misma semilla dé el mismo resultado y que la versión adaptativa corra sin fallar.
- `medir_velocidad.py`: no es una prueba, es un cronómetro. Mide cuánto tarda una calificación para estimar cuánto durará el experimento completo.