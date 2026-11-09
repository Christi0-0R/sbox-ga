'''
Etapa 3.5: calibrar la variante ESTATICA con el mismo esfuerzo que tendrá la adaptativa

Decisiones fijadas ANTES de ver resultados:
  - lam (peso de delta en el fitness) queda FIJO en 2.0 y no entra en la rejilla (R7)
  - N y G salen de config.py (calibración de la etapa 3)
  - rejilla: mutpb x indpb x k = 3 x 3 x 3 = 27 combinaciones
  - semillas: solo las preliminares (nunca las finales)
  - criterio de elección: mayor fitness final medio; si hay varias a menos de
    TOLERANCIA del mejor, se elige la más cercana a la configuración base
    (menor distancia en posiciones de la rejilla), porque es la más simple de justificar

Uso:
  PYTHONPATH=. python experimentos/calibracion_estatica.py              # rejilla completa, 20 semillas
  PYTHONPATH=. python experimentos/calibracion_estatica.py 8            # solo 8 semillas
Es reanudable: omite los CSV que ya existen
'''

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import itertools
import sys
import time
from multiprocessing import Pool

import pandas as pd

from experimentos.config import CFG, SEMILLAS_PRELIM
from src.motor_ga import correr

MUTPB = [0.1, 0.2, 0.4]
INDPB = [0.01, 0.02, 0.05]
K = [2, 3, 5]
BASE = (0.2, 0.02, 3)          # configuración actual de config.py
TOLERANCIA = 0.3               # diferencia de fitness medio que se considera empate
SALIDA = "resultados/calib_estatica"


def _nombre(m, i, k, s):
    return f"{SALIDA}/estatica_m{m}_i{i}_k{k}_{s}.csv"


def _tarea(args):
    m, i, k, s = args
    ruta = _nombre(m, i, k, s)
    t = time.time()
    if not os.path.exists(ruta):
        correr(s, False, dict(CFG, mutpb=m, indpb=i, k=k), ruta + ".tmp")
        os.replace(ruta + ".tmp", ruta)      # el CSV aparece solo si la corrida terminó
    return m, i, k, s, time.time() - t


def _distancia(m, i, k):
    return abs(MUTPB.index(m) - MUTPB.index(BASE[0])) \
         + abs(INDPB.index(i) - INDPB.index(BASE[1])) \
         + abs(K.index(k) - K.index(BASE[2]))


def tabla(semillas, mutpb=MUTPB, indpb=INDPB, k_=K):
    filas = []
    for m, i, k in itertools.product(mutpb, indpb, k_):
        d = [pd.read_csv(_nombre(m, i, k, s)).iloc[-1] for s in semillas]
        filas.append(dict(
            mutpb=m, indpb=i, k=k,
            fit=sum(x.fit_mejor for x in d) / len(d),
            nl=sum(x.nl_mejor for x in d) / len(d),
            delta=sum(x.delta_mejor for x in d) / len(d),
            div=sum(x.diversidad for x in d) / len(d),
            dist=_distancia(m, i, k)))
    return pd.DataFrame(filas).sort_values("fit", ascending=False).reset_index(drop=True)


def elegir(df):
    # Entre las que están a menos de TOLERANCIA del mejor, la más cercana a BASE
    cand = df[df.fit >= df.fit.max() - TOLERANCIA]
    return cand.sort_values(["dist", "fit"], ascending=[True, False]).iloc[0]


if __name__ == "__main__":
    semillas = SEMILLAS_PRELIM[:int(sys.argv[1])] if len(sys.argv) > 1 else SEMILLAS_PRELIM
    tareas = [(m, i, k, s) for (m, i, k) in itertools.product(MUTPB, INDPB, K) for s in semillas]
    print(f"N={CFG['N']} G={CFG['G']} lam={CFG['lam']} | {len(tareas)} corridas", flush=True)

    t0 = time.time()
    with Pool(processes=min(os.cpu_count() or 1, len(tareas))) as pool:
        for n, (m, i, k, s, dt) in enumerate(pool.imap_unordered(_tarea, tareas), 1):
            if n % 20 == 0 or n == len(tareas):
                print(f"{n}/{len(tareas)} listas ({(time.time() - t0) / 60:.1f} min)", flush=True)

    df = tabla(semillas)
    pd.set_option("display.width", 120)
    print("\n", df.round(3).to_string(index=False))
    e = elegir(df)
    print(f"\nELEGIDA: mutpb={e.mutpb} indpb={e.indpb} k={int(e.k)} "
          f"(fit medio {e.fit:.2f}, NL {e.nl:.1f}, delta {e.delta:.1f})")
    print(f"Aviso: elegir el máximo de {len(df)} medias sobreestima un poco el valor real; "
          f"el fitness definitivo se mide con las semillas finales")
