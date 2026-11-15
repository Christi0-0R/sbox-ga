'''
Fase 5b: genera las muestras para probar el cifrado de archivos (carpeta ejemplos/)
Son deterministas: el mismo script produce siempre los mismos bytes

python -m experimentos.generar_muestras
'''

import os
import struct
import sys
import zlib

TEXTO = (
    "La criptografía es una herramienta esencial de la ciberseguridad para proteger "
    "información frente a accesos no autorizados, y se apoya en algoritmos como el Estándar "
    "de Cifrado Avanzado (AES), que operan con claves de 128 o 256 bits. Dentro de AES, las "
    "cajas de sustitución (S-boxes) son el único componente no lineal y determinan la "
    "resistencia de cifrado ante el criptoanálisis lineal y diferencial.\n"
    "\n"
    "La calidad de una S-box se evalúa mediante métricas formales como la no-linealidad (NL) "
    "y la uniformidad diferencial (δ). Dado el enorme espacio de funciones biyectivas sobre "
    "GF(2⁸), la búsqueda exhaustiva es inviable: 256! ≈ 8.58 × 10⁵⁰⁶ permutaciones.\n"
    "\n"
    "Prueba de caracteres: áéíóú ÁÉÍÓÚ ñ Ñ ü ¿? ¡! € « » — … 0123456789\n"
)


def _chunk(tipo, datos):
    cuerpo = tipo + datos
    return struct.pack(">I", len(datos)) + cuerpo + struct.pack(">I", zlib.crc32(cuerpo) & 0xFFFFFFFF)


def png_rgb(ancho=256, alto=256):
    """PNG RGB sin dependencias externas: degradado, un círculo y un rectángulo.
    Usa el filtro "Up" de PNG (cada fila menos la anterior) para que pese pocos KB."""
    filas = bytearray()
    anterior = bytes(ancho * 3)
    for y in range(alto):
        fila = bytearray()
        for x in range(ancho):
            r, g, b = x, y, (x + y) // 2
            if (x - 128) ** 2 + (y - 128) ** 2 < 60 ** 2:
                r, g, b = 255 - x, 200, 255 - y
            if 20 <= x < 80 and 20 <= y < 60:
                r, g, b = 255, 255, 255
            fila += bytes((r, g, b))
        filas.append(2)                        # filtro "Up"
        filas += bytes((a - b) % 256 for a, b in zip(fila, anterior))
        anterior = bytes(fila)
    ihdr = struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(filas), 9)) + _chunk(b"IEND", b""))


def elf_minimo():
    """ELF de x86-64 (Linux) de 129 bytes cuyo unico efecto es terminar con codigo 0:
    xor edi, edi ; mov eax, 60 ; syscall   (exit(0))."""
    codigo = bytes([0x31, 0xFF, 0xB8, 0x3C, 0x00, 0x00, 0x00, 0x0F, 0x05])
    base, ehsize, phsize = 0x400000, 64, 56
    total = ehsize + phsize + len(codigo)
    ident = b"\x7fELF" + bytes([2, 1, 1, 0]) + bytes(8)
    ehdr = ident + struct.pack("<HHIQQQIHHHHHH", 2, 0x3E, 1, base + ehsize + phsize,
                               ehsize, 0, 0, ehsize, phsize, 1, 0, 0, 0)
    phdr = struct.pack("<IIQQQQQQ", 1, 5, 0, base, base, total, total, 0x1000)
    return ehdr + phdr + codigo


MUESTRAS = {
    "texto.txt": lambda: TEXTO.encode("utf-8"),
    "imagen.png": png_rgb,
    "ejecutable_minimo": elf_minimo,
    "vacio.bin": lambda: b"",
}


def generar(directorio="ejemplos"):
    os.makedirs(directorio, exist_ok=True)
    rutas = []
    for nombre, f in MUESTRAS.items():
        ruta = os.path.join(directorio, nombre)
        with open(ruta, "wb") as fh:
            fh.write(f())
        rutas.append(ruta)
    return rutas


if __name__ == "__main__":
    for r in generar(sys.argv[1] if len(sys.argv) > 1 else "ejemplos"):
        print(r, os.path.getsize(r), "bytes")