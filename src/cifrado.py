"""
Esquema de demostracion: sustitucion byte a byte con una S-box de 8x8.

ADVERTENCIA: esto NO es un cifrado seguro. Es una sustitucion monoalfabetica (cada byte
siempre se cambia por el mismo byte), por lo que el analisis de frecuencias la rompe sin
conocer la S-box. Sirve solo para mostrar que una S-box obtenida por el AG se puede usar
como componente de sustitucion y que el proceso es reversible. No usar para proteger datos.
"""
import hashlib


def _validar(sbox):
    s = list(sbox)
    if len(s) != 256 or sorted(s) != list(range(256)):
        raise ValueError("la S-box debe ser una permutacion de 0..255")
    return bytes(s)


def inversa(sbox):
    tabla = _validar(sbox)
    inv = bytearray(256)
    for x, y in enumerate(tabla):
        inv[y] = x
    return bytes(inv)


def cifrar(datos: bytes, sbox) -> bytes:
    return bytes(datos).translate(_validar(sbox))


def descifrar(datos: bytes, sbox) -> bytes:
    return bytes(datos).translate(inversa(sbox))


def sha256(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def cifrar_archivo(ruta_entrada, ruta_salida, sbox, bloque=1 << 20):
    tabla = _validar(sbox)
    with open(ruta_entrada, "rb") as fi, open(ruta_salida, "wb") as fo:
        while chunk := fi.read(bloque):
            fo.write(chunk.translate(tabla))


def descifrar_archivo(ruta_entrada, ruta_salida, sbox, bloque=1 << 20):
    tabla = inversa(sbox)
    with open(ruta_entrada, "rb") as fi, open(ruta_salida, "wb") as fo:
        while chunk := fi.read(bloque):
            fo.write(chunk.translate(tabla))