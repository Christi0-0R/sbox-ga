import os
import random

import pytest

from src.cifrado import (cifrar, descifrar, inversa, sha256,
                         cifrar_archivo, descifrar_archivo)
from src.gf256 import aes_sbox


def _perm(semilla):
    p = list(range(256))
    random.Random(semilla).shuffle(p)
    return p


@pytest.mark.parametrize("datos", [
    b"",
    "Hola mundo, áéíóú ñ".encode("utf-8"),
    bytes(range(256)),
    random.Random(1).randbytes(5000),
])
def test_ida_y_vuelta_con_sha256(datos):
    for sb in (aes_sbox(), _perm(3)):
        c = cifrar(datos, sb)
        assert len(c) == len(datos)
        assert sha256(descifrar(c, sb)) == sha256(datos)


def test_cifrar_cambia_los_datos_y_usa_la_tabla():
    sb = _perm(5)
    datos = bytes(range(256))
    assert cifrar(datos, sb) == bytes(sb)          # byte x -> sbox[x]
    assert cifrar(datos, sb) != datos


def test_aes_valores_conocidos():
    # S-box de AES: 0x00 -> 0x63, 0x01 -> 0x7c, 0x53 -> 0xed
    assert cifrar(bytes([0x00, 0x01, 0x53]), aes_sbox()) == bytes([0x63, 0x7C, 0xED])


def test_inversa_es_inversa():
    sb = _perm(9)
    inv = inversa(sb)
    assert all(inv[sb[x]] == x for x in range(256))


def test_rechaza_sbox_invalida():
    with pytest.raises(ValueError):
        cifrar(b"a", [0] * 256)            # no es permutacion
    with pytest.raises(ValueError):
        cifrar(b"a", list(range(255)))     # largo incorrecto


def test_archivo_binario_ida_y_vuelta(tmp_path):
    datos = random.Random(2).randbytes(3_000_000)  # > un bloque de 1 MiB
    a, b, c = (str(tmp_path / n) for n in ("a.bin", "b.bin", "c.bin"))
    with open(a, "wb") as f:
        f.write(datos)
    sb = _perm(11)
    cifrar_archivo(a, b, sb)
    descifrar_archivo(b, c, sb)
    with open(b, "rb") as f:
        assert f.read() != datos
    with open(c, "rb") as f:
        assert sha256(f.read()) == sha256(datos)