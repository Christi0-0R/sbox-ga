# Cifrado de archivos con las S-boxes finales (Fase 5b)

## experimentos/generar_muestras.py

Genera de forma determinista los archivos de `ejemplos/`:

| Archivo | Contenido | Tamaño |
|---|---|---|
| `texto.txt` | Texto en español con acentos y símbolos | 769 B |
| `imagen.png` | PNG RGB de 256×256, construido a mano (chunks y CRC) | 3222 B |
| `ejecutable_minimo` | ELF x86-64 mínimo que termina con código 0 | 129 B |
| `vacio.bin` | Archivo vacío | 0 B |

Además, cada corrida de `cifrar_archivos.py` genera 1 MiB de bytes aleatorios con semilla fija (no se guarda en el repo).

## experimentos/cifrar_archivos.py

1. **Elige la mejor S-box de cada variante** con una regla fijada antes de ver resultados: mayor fitness; en empate, menor δ; en empate, menor semilla. Suma AES como referencia.
2. **Cifra y descifra** cada archivo con `src/cifrado.py` (3 S-boxes × 5 archivos = 15 combinaciones).
3. **Comprueba**, por combinación: SHA-256 del recuperado = SHA-256 del original; el cifrado es distinto del original (salvo el vacío); el ejecutable recuperado corre y termina con código 0 (solo en Linux; en otros sistemas queda `n/a`).
4. **Escribe** `resultados/cifrado/cifrado_archivos.csv` y `comparacion_sboxes.csv`, y sale con error si alguna combinación falla.

## Resultado

| S-box | Semilla | NL | δ | Fitness |
|---|---|---|---|---|
| Mejor estática | 1008 | 100 | 8 | 92.0 |
| Mejor adaptativa | 1036 | 100 | 8 | 92.0 |
| AES | – | 112 | 4 | 112.0 |

15/15 combinaciones recuperan el archivo idéntico.

## Lo que esto demuestra y lo que no

- Sí: las S-boxes del AG son biyectivas, reversibles y utilizables como componente de sustitución sobre archivos binarios reales.
- No: que protejan datos. La sustitución byte a byte conserva las frecuencias y no es segura por sí sola. Las "mejores" S-boxes son el máximo de 100 corridas, no una S-box típica.
