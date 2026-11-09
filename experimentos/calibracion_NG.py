'''
Etapa 3: ¿con qué (N, G) el AG estático supera a la búsqueda aleatoria?

Criterios fijados ANTES de ver resultados:
  (a) fitness final de la estática > aleatoria (Mann-Whitney unilateral, p < 0.05)
  (b) estancamiento: en >= 50 % de las corridas el mejor no mejora durante el
      último 20 % de las generaciones (si sigue mejorando hasta el final, la
      adaptativa no tendría nada que corregir)
Se elige la configuración MÁS BARATA (N x G) que cumpla (a) y (b)

Uso:
  PYTHONPATH=. python experimentos/calibracion_NG.py                   # combos y semillas por defecto
  PYTHONPATH=. python experimentos/calibracion_NG.py 100x100,100x200   # combos propios
  PYTHONPATH=. python experimentos/calibracion_NG.py 100x100 8         # solo las primeras 8 semillas
Es reanudable: omite los CSV que ya existen
'''

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import time
from multiprocessing import Pool

import pandas as pd
from scipy.stats import mannwhitneyu

from experimentos.config import CFG, SEMILLAS_PRELIM
from experimentos.baseline_aleatoria import correr_aleatoria
from src.motor_ga import correr

COMBOS_DEFECTO = [(100, 100), (100, 200), (200, 200)]
SALIDA = "resultados/calib_NG"


def _tarea(args):
    N, G, semilla = args
    cfg = dict(CFG, N=N, G=G)
    ruta_e = f"{SALIDA}/estatica_N{N}_G{G}_{semilla}.csv"
    ruta_a = f"{SALIDA}/aleatoria_N{N}_G{G}_{semilla}.csv"
    t = time.time()
    if not os.path.exists(ruta_e):
        correr(semilla, False, cfg, ruta_e)
    if not os.path.exists(ruta_a):
        correr_aleatoria(semilla, cfg, ruta_a)
    return N, G, semilla, time.time() - t


def resumen(combos, semillas):
    print(f"\n{'N':>4} {'G':>4} | {'fit_ini':>7} {'fit_est':>7} {'fit_ale':>7} | "
          f"{'p (est>ale)':>11} | {'(a)':>3} {'estanc.':>7} {'(b)':>3} | {'NL_est':>6} {'d_est':>5}")
    for N, G in combos:
        est, ale, ini, estanc, nl_e, d_e = [], [], [], 0, [], []
        for s in semillas:
            e = pd.read_csv(f"{SALIDA}/estatica_N{N}_G{G}_{s}.csv")
            a = pd.read_csv(f"{SALIDA}/aleatoria_N{N}_G{G}_{s}.csv")
            est.append(e.fit_mejor.iloc[-1]); ale.append(a.fit_mejor.iloc[-1])
            ini.append(e.fit_mejor.iloc[0])
            nl_e.append(e.nl_mejor.iloc[-1]); d_e.append(e.delta_mejor.iloc[-1])
            k = int(0.8 * G)
            estanc += int(e.fit_mejor.iloc[-1] == e.fit_mejor.iloc[k])
        n = len(semillas)
        p = mannwhitneyu(est, ale, alternative="greater").pvalue
        ok_a = p < 0.05
        ok_b = estanc / n >= 0.5
        print(f"{N:>4} {G:>4} | {sum(ini)/n:7.2f} {sum(est)/n:7.2f} {sum(ale)/n:7.2f} | "
              f"{p:11.4f} | {'SI' if ok_a else 'no':>3} {estanc/n:7.0%} {'SI' if ok_b else 'no':>3} | "
              f"{sum(nl_e)/n:6.1f} {sum(d_e)/n:5.1f}")


if __name__ == "__main__":
    combos = COMBOS_DEFECTO
    if len(sys.argv) > 1:
        combos = [tuple(int(x) for x in c.split("x")) for c in sys.argv[1].split(",")]
    semillas = SEMILLAS_PRELIM[:int(sys.argv[2])] if len(sys.argv) > 2 else SEMILLAS_PRELIM

    tareas = [(N, G, s) for (N, G) in combos for s in semillas]
    t0 = time.time()
    with Pool(processes=min(os.cpu_count() or 1, len(tareas))) as pool:
        for N, G, s, dt in pool.imap_unordered(_tarea, tareas):
            print(f"N={N} G={G} semilla={s}: {dt:.0f} s", flush=True)
    print(f"Tiempo total: {(time.time() - t0) / 60:.1f} min")
    resumen(combos, semillas)