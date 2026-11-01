'''
Módulo 2:
evaluador criptográfico (DDT, Walsh/LAT, NL, delta, fitness)
'''

import numpy as np

_X = np.arange(256)
_PAR = np.array([bin(i).count("1") & 1 for i in range(256)], dtype = np.int64)
# Matriz de Hadamard: H[a, x] = (-1)^(ax)
_H = (1 - 2 * _PAR[np.bitwise_and.outer(_X, _X)]).astype(np.float64)
_FILAS = (np.arange(256) * 256)[:, None]


def es_permutacion(sbox):
    return sorted(int(v) for v in sbox) == list(range(256))

def ddt(sbox):
    # Tabla de distribucion de diferencias T[dx, dy]
    s = np.asarray(sbox, dtype = np.int64)
    dy = s[None, :] ^ s[_X[None, :] ^ _X[:, None]] # dy[dx, x] = S(x) ^ S(x^dx)
    return np.bincount((_FILAS + dy).ravel(), minlength = 65536).reshape(256, 256)

def delta(sbox):
    # Uniformidad diferencial: maximo de la DDT sin la fila dx = 0
    return int(ddt(sbox)[1:].max())

def walsh(sbox):
    # Espectro de Walsh W[a, b] = sum_x (-1)^(ax + bS(x)). LAT = W/2
    s = np.asarray(sbox, dtype = np.int64)
    F = (1 - 2 * _PAR[np.bitwise_and.outer(s, _X)]).astype(np.float64)  # F[x, b]
    return np.rint(_H @ F).astype(np.int64)

def nl(sbox):
    # No-linealidad: 128 - max | W(a, b) | / 2, con b != 0
    W = walsh(sbox)
    return int(128 - np.abs(W[:, 1:]).max() // 2)

# Provisional: se fija con las corridas preliminares (riesgo R7)
LAMBDA = 2.0

def fitness(sbox, lam = LAMBDA):
    # Mono-objetivo agregado: NL - lam * (delta - 4)
    return float(nl(sbox) - lam * (delta(sbox) - 4))

