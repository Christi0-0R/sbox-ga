'''
Módulo 3:
motor evolutivo (AG de permutación estático y adaptativo) con DEAP
'''

import copy
import csv
import os
import random

import numpy as np
from deap import base, creator, tools

from src.evaluador import metricas, fitness_de

if not hasattr(creator, "FitnessMax"):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

N_PARES_DIV = 100  # pares muestreados para estimar la diversidad


def _evaluar(ind, lam):
    # Calcula NL y delta una vez, los guarda en el individuo y fija su fitness
    n, d = metricas(ind)
    ind.nl, ind.delta = n, d
    ind.fitness.values = (fitness_de(n, d, lam),)


def diversidad(pop, rng):
    '''
    Distancia de Hamming media normalizada entre N_PARES_DIV pares al azar
    0 = todos iguales; cercano a 1 = muy distintos
    Usa su propio generador (rng) para no alterar la secuencia aleatoria de la evolución
    '''

    n = len(pop)
    total = 0.0
    for _ in range(N_PARES_DIV):
        i, j = rng.sample(range(n), 2)
        total += sum(a != b for a, b in zip(pop[i], pop[j])) / 256.0
    return total / N_PARES_DIV


def explorando(p, cfg):
    # La variante está en modo explorar si usa el tamaño de torneo de exploración
    return cfg["k_explorar"] != cfg["k"] and p["k"] == cfg["k_explorar"]


def actualizar_parametros(p, ind, cfg):
    '''
    Regla de la variante adaptativa (función pura, no modifica sus argumentos)
    p:   parámetros vigentes {mutpb, indpb, k}
    ind: indicadores {sin_mejora_nl, sin_mejora_delta, div}
    Dos modos, con histéresis para que no se quede atorada en uno:
      EXPLOTAR (parámetros base, los de la estática). Pasa a explorar si la búsqueda
        está estancada (NL y delta >= ventana generaciones sin mejorar su mejor valor)
        o si la diversidad cae por debajo de div_min
      EXPLORAR: sube mutpb e indpb (hasta sus topes) y baja el torneo a k_explorar.
        Regresa a explotar cuando la diversidad se recupera (>= div_rec)
    '''

    if explorando(p, cfg) and ind["div"] >= cfg["div_rec"]:
        return dict(mutpb=cfg["mutpb"], indpb=cfg["indpb"], k=cfg["k"])
    estancada = (ind["sin_mejora_nl"] >= cfg["ventana"]
                 and ind["sin_mejora_delta"] >= cfg["ventana"])
    if explorando(p, cfg) or estancada or ind["div"] < cfg["div_min"]:
        return dict(mutpb=min(p["mutpb"] * cfg["factor"], cfg["mutpb_max"]),
                    indpb=min(p["indpb"] * cfg["factor"], cfg["indpb_max"]),
                    k=cfg["k_explorar"])
    return dict(p)


def _descendencia(pop, cxpb, mutpb, indpb, k, lam):
    '''
    Selección por torneo, cruce PMX, mutación y evaluación de los descendientes
    Todo individuo que sale de aquí tiene fitness, NL y delta vigentes
    '''

    off = tools.selTournament(pop, len(pop), tournsize=k)
    off = [copy.deepcopy(i) for i in off]
    for a, b in zip(off[::2], off[1::2]):
        if random.random() < cxpb:
            tools.cxPartialyMatched(a, b)
            del a.fitness.values
            del b.fitness.values
    for ind in off:
        if random.random() < mutpb:
            tools.mutShuffleIndexes(ind, indpb=indpb)
            del ind.fitness.values
    for ind in off:
        if not ind.fitness.valid:
            _evaluar(ind, lam)
    return off


def correr(semilla, adaptativo, cfg, ruta_csv):
    random.seed(semilla)
    rng_div = random.Random(semilla + 7919)   # generador independiente para la diversidad

    pop = []
    for _ in range(cfg["N"]):
        perm = list(range(256))
        random.shuffle(perm)
        pop.append(creator.Individual(perm))
    lam = cfg["lam"]
    for ind in pop:
        _evaluar(ind, lam)

    hof = tools.HallOfFame(1)
    hof.update(pop)

    cxpb = cfg["cxpb"]
    par = dict(mutpb=cfg["mutpb"], indpb=cfg["indpb"], k=cfg["k"])
    mejor_hist = hof[0].fitness.values[0]
    nl_hist = max(i.nl for i in pop)          # mejor NL de la población, histórico
    delta_hist = min(i.delta for i in pop)    # mejor delta de la población, histórico
    sin_mejora = sin_mejora_nl = sin_mejora_delta = 0
    nombre = "adaptativa" if adaptativo else "estatica"
    filas = []

    for g in range(cfg["G"] + 1):
        mejor = hof[0]
        fits = [i.fitness.values[0] for i in pop]
        div = diversidad(pop, rng_div)

        # contador de estancamiento (se compara antes de actualizar el histórico)
        if g > 0:
            if mejor.fitness.values[0] > mejor_hist:
                mejor_hist = mejor.fitness.values[0]
                sin_mejora = 0
            else:
                sin_mejora += 1
            if max(i.nl for i in pop) > nl_hist:
                nl_hist = max(i.nl for i in pop)
                sin_mejora_nl = 0
            else:
                sin_mejora_nl += 1
            if min(i.delta for i in pop) < delta_hist:
                delta_hist = min(i.delta for i in pop)
                sin_mejora_delta = 0
            else:
                sin_mejora_delta += 1

        filas.append(dict(
            variante=nombre, semilla=semilla, generacion=g,
            fit_mejor=mejor.fitness.values[0], fit_max_pob=max(fits),
            fit_prom=float(np.mean(fits)),
            nl_mejor=mejor.nl, delta_mejor=mejor.delta,
            nl_max_pob=max(i.nl for i in pop), delta_min_pob=min(i.delta for i in pop),
            nl_prom=float(np.mean([i.nl for i in pop])),
            delta_prom=float(np.mean([i.delta for i in pop])),
            diversidad=round(div, 6), sin_mejora=sin_mejora,
            sin_mejora_nl=sin_mejora_nl, sin_mejora_delta=sin_mejora_delta,
            mutpb=par["mutpb"], indpb=par["indpb"], k=par["k"], cxpb=cxpb))
        if g == cfg["G"]:
            break

        # ÚNICA diferencia entre variantes:
        if adaptativo:
            antes = explorando(par, cfg)
            par = actualizar_parametros(
                par, dict(sin_mejora_nl=sin_mejora_nl,
                          sin_mejora_delta=sin_mejora_delta, div=div), cfg)
            if antes and not explorando(par, cfg):
                # terminó una fase de exploración: el estancamiento se mide desde cero
                sin_mejora_nl = sin_mejora_delta = 0

        # selección, cruce, mutación
        off = _descendencia(pop, cxpb, par["mutpb"], par["indpb"], par["k"], lam)

        # elitismo: el mejor histórico sustituye al peor de la nueva generación
        elite = copy.deepcopy(hof[0])
        off.sort(key=lambda i: i.fitness.values[0])
        off[0] = elite
        pop = off
        hof.update(pop)

    d = os.path.dirname(ruta_csv)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(ruta_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    return hof[0]