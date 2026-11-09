'''
Etapa 4.4: calibrar los umbrales de la variante ADAPTATIVA

Decisiones fijadas ANTES de ver resultados (mismo presupuesto que la estática):
  - rejilla: ventana x div_min x factor = 3 x 3 x 3 = 27 combinaciones
  - semillas: solo las preliminares (nunca las finales)
  - N, G, lam, mutpb/indpb/k base, topes y k_explorar salen de config.py y no se tocan
  - COMPUERTA (la configuración debe moverse de verdad). Para ser elegible:
      * fracción media de generaciones en modo explorar entre 5 % y 70 %
        (menos: el control casi no actúa; más: la búsqueda se vuelve casi aleatoria)
  - criterio de elección entre las elegibles: mayor fitness final medio; si hay varias
    a menos de TOLERANCIA del mejor, la más "simple" = factor menor, luego ventana
    mayor, luego div_min menor (la que menos se aleja de la estática)
  - Si ninguna es elegible, NO se ajusta el criterio: se reporta y se rediseña la regla
Se corre también la estática calibrada en las mismas semillas, solo como referencia
(no interviene en la elección)

Uso:
  PYTHONPATH=. python experimentos/calibracion_adaptativa.py       # 20 semillas
  PYTHONPATH=. python experimentos/calibracion_adaptativa.py 8     # solo 8 semillas
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

VENTANA = [5, 10, 20]
DIV_MIN = [0.05, 0.15, 0.30]
FACTOR = [1.25, 1.5, 2.0]
TOLERANCIA = 0.3                  # diferencia de fitness medio que se considera empate
EXPLORA_MIN, EXPLORA_MAX = 0.05, 0.70
SALIDA = "resultados/calib_adaptativa"


def _nombre(v, d, f, s):
    return f"{SALIDA}/adaptativa_v{v}_d{d}_f{f}_{s}.csv"


def _ref(s):
    return f"{SALIDA}/estatica_ref_{s}.csv"


def _tarea(args):
    v, d, f, s = args
    if v is None:                                  # corrida de referencia: la estática calibrada
        ruta, adaptativo, cfg = _ref(s), False, CFG
    else:
        ruta, adaptativo = _nombre(v, d, f, s), True
        cfg = dict(CFG, ventana=v, div_min=d, factor=f)
    if not os.path.exists(ruta):
        correr(s, adaptativo, cfg, ruta + ".tmp")
        os.replace(ruta + ".tmp", ruta)            # el CSV aparece solo si la corrida terminó
    return v, d, f, s


def tabla(semillas, ventana=VENTANA, div_min=DIV_MIN, factor=FACTOR, k_explorar=None):
    k_explorar = CFG["k_explorar"] if k_explorar is None else k_explorar
    filas = []
    for v, d, f in itertools.product(ventana, div_min, factor):
        dfs = [pd.read_csv(_nombre(v, d, f, s)) for s in semillas]
        ult = [x.iloc[-1] for x in dfs]
        filas.append(dict(
            ventana=v, div_min=d, factor=f,
            fit=sum(u.fit_mejor for u in ult) / len(ult),
            nl=sum(u.nl_mejor for u in ult) / len(ult),
            delta=sum(u.delta_mejor for u in ult) / len(ult),
            explora=sum((x.k == k_explorar).mean() for x in dfs) / len(dfs),
            mutpb_medio=sum(x.mutpb.mean() for x in dfs) / len(dfs)))
    df = pd.DataFrame(filas)
    df["elegible"] = df.explora.between(EXPLORA_MIN, EXPLORA_MAX)
    return df.sort_values("fit", ascending=False).reset_index(drop=True)


def elegir(df):
    # Devuelve la fila elegida, o None si ninguna pasa la compuerta
    el = df[df.elegible]
    if el.empty:
        return None
    cand = el[el.fit >= el.fit.max() - TOLERANCIA]
    return cand.sort_values(["factor", "ventana", "div_min"],
                            ascending=[True, False, True]).iloc[0]


if __name__ == "__main__":
    semillas = SEMILLAS_PRELIM[:int(sys.argv[1])] if len(sys.argv) > 1 else SEMILLAS_PRELIM
    tareas = [(v, d, f, s) for (v, d, f) in itertools.product(VENTANA, DIV_MIN, FACTOR) for s in semillas]
    tareas += [(None, None, None, s) for s in semillas]
    print(f"N={CFG['N']} G={CFG['G']} lam={CFG['lam']} | {len(tareas)} corridas", flush=True)

    t0 = time.time()
    with Pool(processes=min(os.cpu_count() or 1, len(tareas))) as pool:
        for n, _ in enumerate(pool.imap_unordered(_tarea, tareas), 1):
            if n % 20 == 0 or n == len(tareas):
                print(f"{n}/{len(tareas)} listas ({(time.time() - t0) / 60:.1f} min)", flush=True)

    df = tabla(semillas)
    pd.set_option("display.width", 130)
    print("\n", df.round(3).to_string(index=False))
    ref = [pd.read_csv(_ref(s)).iloc[-1] for s in semillas]
    print(f"\nReferencia (estática calibrada, mismas semillas): fit {sum(r.fit_mejor for r in ref)/len(ref):.2f}, "
          f"NL {sum(r.nl_mejor for r in ref)/len(ref):.1f}, delta {sum(r.delta_mejor for r in ref)/len(ref):.1f}")
    e = elegir(df)
    if e is None:
        print("\nNINGUNA configuración pasa la compuerta (explora entre "
              f"{EXPLORA_MIN:.0%} y {EXPLORA_MAX:.0%}). No se ajusta el criterio: hay que rediseñar la regla")
    else:
        print(f"\nELEGIDA: ventana={int(e.ventana)} div_min={e.div_min} factor={e.factor} "
              f"(fit medio {e.fit:.2f}, NL {e.nl:.1f}, delta {e.delta:.1f}, explora {e.explora:.0%})")
    print("Aviso: elegir el máximo de 27 medias sobreestima un poco el valor real; "
          "el fitness definitivo se mide con las semillas finales")