'''
Módulo 4 (parte):
implementaciones independientes para contrastar el evaluador
'''

def delta_directo(sbox):
    # δ por conteo directo de pares, sin NumPy
    mejor = 0
    for dx in range(1, 256):
        cuenta = [0] * 256
        for x in range(256):
            cuenta[sbox[x] ^ sbox[x ^ dx]] += 1
        mejor = max(mejor, max(cuenta))
    return mejor

def _fwht(v):
    # Transformada rapida de Walsh - Hadamard (sin normalizar)
    v = list(v)
    h = 1
    while h < len(v):
        for i in range(0, len(v), h * 2):
            for j in range(i, i + h):
                a, b = v[j], v[j + h]
                v[j], v[j + h] = a + b, a - b
        h *= 2
    return v

def nl_fwht(sbox):
    # NL con una FWHT por cada funcion componente bS (b != 0)
    mejor = 0
    for b in range(1, 256):
        f = [1 - 2 * (bin(sbox[x] & b).count("1") & 1) for x in range(256)]
        mejor = max(mejor, max(abs(t) for t in _fwht(f)))
    return 128 - mejor // 2