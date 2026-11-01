'''
Módulo 1:
álgebra de GF(2^8) con polinomio irreducible x^8+x^4+x^3+x+1 (0x11B)
'''

POLY = 0x11B

def gf_mul(a, b):
    # multiplicacion en GF(2^8)
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= POLY
        b >>= 1
    return r

def gf_inv(a):
    # inverso multiplicativo, por convencion de AES, inv(0) = 0
    if a == 0:
        return 0
    for b in range(1, 256):
        if gf_mul(a, b) == 1:
            return b

def _rotl8(x, n):
    return ((x << n) | (x >> (8 - n))) & 0xFF

def affine(x):
    # transformacion afin de AES
    return x ^ _rotl8(x, 1) ^ _rotl8(x, 2) ^ _rotl8(x, 3) ^ _rotl8(x, 4) ^ 0x63

def aes_sbox():
    # S-box de AES como lista de 256 enteros
    return [affine(gf_inv(x)) for x in range(256)]