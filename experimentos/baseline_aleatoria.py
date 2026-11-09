'''
Referencia de sanidad: búsqueda aleatoria con el MISMO presupuesto que el AG

Genera N x (G + 1) permutaciones al azar, agrupadas en G + 1 "generaciones" de N
Con la misma semilla, las primeras N permutaciones son idénticas a la población
inicial del AG (ambos usan random.seed + random.shuffle), así que comparten el
punto de partida. Es una referencia, no una tercera hipótesis
Nota: el AG evalúa algo menos que N x (G + 1) (no reevalúa al elite ni a los
descendientes sin cambios), así que la referencia recibe un presupuesto igual o mayor
'''

import csv
import os
import random

import numpy as np

from src.evaluador import metricas


def flujo_aleatorio(semilla, n_evals, lam):
    # n_evals permutaciones aleatorias evaluadas, en el orden en que se generan
    random.seed(semilla)
    nls = np.empty(n_evals, dtype=np.int64)
    deltas = np.empty(n_evals, dtype=np.int64)
    for i in range(n_evals):
        perm = list(range(256))
        random.shuffle(perm)
        nls[i], deltas[i] = metricas(perm)
    fits = nls - lam * (deltas - 4)
    return fits.astype(np.float64), nls, deltas


def correr_aleatoria(semilla, cfg, ruta_csv):
    N, G = cfg["N"], cfg["G"]
    fits, nls, deltas = flujo_aleatorio(semilla, N * (G + 1), cfg["lam"])

    filas = []
    mejor = 0   # índice del mejor hasta ahora (el primero en caso de empate)
    for g in range(G + 1):
        a, b = g * N, (g + 1) * N
        j = a + int(np.argmax(fits[a:b]))
        if fits[j] > fits[mejor]:
            mejor = j
        filas.append(dict(
            variante="aleatoria", semilla=semilla, generacion=g,
            fit_mejor=float(fits[mejor]), fit_max_pob=float(fits[a:b].max()),
            fit_prom=float(fits[a:b].mean()),
            nl_mejor=int(nls[mejor]), delta_mejor=int(deltas[mejor]),
            nl_prom=float(nls[a:b].mean()), delta_prom=float(deltas[a:b].mean())))

    d = os.path.dirname(ruta_csv)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(ruta_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    return filas[-1]