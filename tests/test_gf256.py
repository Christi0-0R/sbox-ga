from src.gf256 import gf_mul, gf_inv, aes_sbox

def test_valores_conocidos():
    s = aes_sbox()
    assert s[0x00] == 0x63
    assert s[0x01] == 0x7C
    assert s[0x53] == 0xED

def test_es_permutacion():
    assert sorted(aes_sbox()) == list(range(256))

def test_inverso():
    for a in range(1, 256):
        assert gf_mul(a, gf_inv(a)) == 1

def test_multiplicacion_ejemplo_fips197():
    # Ejemplo de la especificacion de AES: {57} x {83} = {c1}
    assert gf_mul(0x57, 0x83) == 0xC1