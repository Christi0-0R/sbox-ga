# src/cifrado.py (Módulo 5: sustitución byte a byte)

**Para qué existe:** mostrar que una S-box obtenida por el AG se puede usar como componente de sustitución sobre archivos binarios reales y que el proceso es reversible (OE6).

> **No es un cifrado seguro.** Es una sustitución monoalfabética: cada byte siempre se cambia por el mismo byte, así que conserva las frecuencias del archivo y un análisis de frecuencias la rompe sin conocer la S-box. Es solo demostrativo.

## Funciones

| Función | Qué hace |
|---|---|
| `_validar(sbox)` | Lanza `ValueError` si la S-box no es una permutación de 0 … 255; devuelve la tabla como `bytes`. |
| `inversa(sbox)` | Construye `S⁻¹` tal que `S⁻¹[S[x]] = x`. |
| `cifrar(datos, sbox)` / `descifrar(datos, sbox)` | `bytes.translate` con la tabla o con su inversa. |
| `sha256(datos)` | Hash hexadecimal con `hashlib`, para comprobar la recuperación exacta. |
| `cifrar_archivo` / `descifrar_archivo` | Igual, pero por bloques de 1 MiB, para archivos grandes. |

## Cómo se verifica (`tests/test_cifrado.py`)

Ida y vuelta con SHA-256 idéntico (texto, vacío, binario aleatorio de 3 MB), que el cifrado sí cambie los datos, valores conocidos con la S-box de AES, que la inversa sea inversa y que rechace S-boxes inválidas.

El uso con las S-boxes finales está en `Experimentos/cifrado_archivos.md`.
