"""
Fase 3 del protocolo: corridas finales.

Corre las tres variantes (estatica, adaptativa, aleatoria) con las mismas semillas.
- Reanudable: una corrida con CSV ya terminado se salta (el CSV es la marca de "terminada").
- Escritura atomica: el CSV se escribe como .tmp y se renombra al final (os.replace).
- Guarda la mejor S-box de cada corrida en <dir>/sboxes/<variante>_<semilla>.json
- Guarda meta.json (configuracion, semillas, commit, fecha) y entorno.txt (pip freeze).
- Se niega a correr con una configuracion distinta a la congelada (salvo --smoke).

Uso:
    python -m experimentos.correr_todo                 # 300 corridas finales
    python -m experimentos.correr_todo --smoke         # prueba rapida, no es resultado
    python -m experimentos.correr_todo --workers 4
"""
import os

# Un hilo por proceso: el paralelismo lo da el Pool, no BLAS
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import datetime
import json
import subprocess
import sys
import time
from multiprocessing import Pool

from experimentos.config import CFG, SEMILLAS_FINALES

VARIANTES = ("estatica", "adaptativa", "aleatoria")

# Configuracion congelada para las corridas finales (ver README, Fases 3 y 4)
CFG_CONGELADA = dict(
    N=100, G=100, cxpb=0.9, mutpb=0.4, indpb=0.02, k=5, lam=2.0,
    k_explorar=3, mutpb_max=0.8, indpb_max=0.1, div_rec=0.6,
    ventana=20, div_min=0.05, factor=2.0,
)


def _escribir_json_atomico(ruta, obj):
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, ruta)


def ruta_csv(directorio, variante, semilla):
    return os.path.join(directorio, f"{variante}_{semilla}.csv")


def ruta_sbox(directorio, variante, semilla):
    return os.path.join(directorio, "sboxes", f"{variante}_{semilla}.json")


def _tarea(args):
    variante, semilla, directorio, cfg = args
    final = ruta_csv(directorio, variante, semilla)
    if os.path.exists(final):
        return variante, semilla, "saltada", 0.0
    t0 = time.time()
    tmp = final + ".tmp"
    if variante == "aleatoria":
        from experimentos.baseline_aleatoria import correr_aleatoria
        mejor = correr_aleatoria(semilla, cfg, tmp)
    else:
        from src.motor_ga import correr
        mejor = correr(semilla, variante == "adaptativa", cfg, tmp)
    if mejor is not None and hasattr(mejor, "__len__") and len(mejor) == 256:
        from src.evaluador import metricas
        nl_, d_ = metricas(list(mejor))
        os.makedirs(os.path.join(directorio, "sboxes"), exist_ok=True)
        _escribir_json_atomico(ruta_sbox(directorio, variante, semilla), dict(
            variante=variante, semilla=semilla, sbox=[int(x) for x in mejor],
            nl=int(nl_), delta=int(d_), fitness=float(nl_ - cfg["lam"] * (d_ - 4))))
    os.replace(tmp, final)          # ultimo paso: marca la corrida como terminada
    return variante, semilla, "ok", time.time() - t0


def _commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None


def _guardar_meta(directorio, cfg, semillas, variantes):
    ruta = os.path.join(directorio, "meta.json")
    previa = None
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            previa = json.load(f)
        if previa.get("cfg") != cfg:
            raise SystemExit(
                f"{ruta} tiene otra configuracion: no se mezclan corridas de configuraciones "
                "distintas. Usa otro directorio o borra el anterior a proposito.")
    meta = dict(cfg=cfg, semillas=[min(semillas), max(semillas), len(semillas)],
                variantes=list(variantes), commit=_commit(),
                python=sys.version.split()[0],
                inicio=(previa or {}).get("inicio", datetime.datetime.now().isoformat(timespec="seconds")),
                ultima_ejecucion=datetime.datetime.now().isoformat(timespec="seconds"))
    _escribir_json_atomico(ruta, meta)
    try:
        out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"],
                                      stderr=subprocess.DEVNULL, text=True)
        with open(os.path.join(directorio, "entorno.txt"), "w", newline="\n") as f:
            f.write(out)
    except Exception:
        pass


def correr_todo(directorio, cfg, semillas, variantes=VARIANTES, workers=None):
    os.makedirs(directorio, exist_ok=True)
    _guardar_meta(directorio, cfg, semillas, variantes)
    tareas = [(v, s, directorio, cfg) for s in semillas for v in variantes]
    pendientes = [t for t in tareas if not os.path.exists(ruta_csv(directorio, t[0], t[1]))]
    print(f"{len(tareas)} corridas en total, {len(tareas) - len(pendientes)} ya terminadas, "
          f"{len(pendientes)} por correr", flush=True)
    # limpia .tmp huerfanos de una ejecucion interrumpida
    for nombre in os.listdir(directorio):
        if nombre.endswith(".csv.tmp"):
            os.remove(os.path.join(directorio, nombre))
    t0 = time.time()
    hechas = 0
    if workers == 1:
        resultados = map(_tarea, pendientes)
        pool = None
    else:
        pool = Pool(workers)
        resultados = pool.imap_unordered(_tarea, pendientes, chunksize=1)
    try:
        for v, s, estado, dur in resultados:
            hechas += 1
            if hechas % 10 == 0 or hechas == len(pendientes):
                el = time.time() - t0
                falta = el / hechas * (len(pendientes) - hechas)
                print(f"[{hechas}/{len(pendientes)}] {el/60:.1f} min, faltan ~{falta/60:.1f} min",
                      flush=True)
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    faltan = [t for t in tareas if not os.path.exists(ruta_csv(directorio, t[0], t[1]))]
    print("TERMINADO" if not faltan else f"FALTAN {len(faltan)} corridas", flush=True)
    return len(faltan)


# Diseno del experimento suplementario, declarado ANTES de correrlo (exploratorio):
# solo cambia G; N, parametros y lam son los congelados. Semillas = las primeras n finales.
SUPLEMENTARIO = dict(G=300, n_semillas=40)


def configuracion(a):
    """Devuelve (cfg, semillas, directorio) segun los argumentos. Pura, para poder probarla."""
    if a.smoke and a.suplementario:
        raise SystemExit("--smoke y --suplementario no se combinan")
    if a.smoke:
        return dict(CFG, N=20, G=10), SEMILLAS_FINALES[:3], a.dir or "resultados/smoke"
    cfg = dict(CFG)
    if cfg != CFG_CONGELADA:
        dif = {k: (cfg.get(k), CFG_CONGELADA[k]) for k in CFG_CONGELADA if cfg.get(k) != CFG_CONGELADA[k]}
        raise SystemExit(f"config.py no coincide con la configuracion congelada "
                         f"(actual, congelada): {dif}")
    if a.suplementario:
        cfg = dict(CFG_CONGELADA, G=a.G if a.G is not None else SUPLEMENTARIO["G"])
        n = a.n_semillas if a.n_semillas is not None else SUPLEMENTARIO["n_semillas"]
        if cfg["G"] == CFG_CONGELADA["G"]:
            raise SystemExit("el suplementario debe usar una G distinta de la final")
        if not 1 <= n <= len(SEMILLAS_FINALES):
            raise SystemExit(f"n_semillas debe estar entre 1 y {len(SEMILLAS_FINALES)}")
        return cfg, SEMILLAS_FINALES[:n], a.dir or f"resultados/suplementario_G{cfg['G']}"
    if a.G is not None or a.n_semillas is not None:
        raise SystemExit("--G y --n-semillas solo se permiten con --suplementario")
    return cfg, SEMILLAS_FINALES, a.dir or "resultados/final"


def principal(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None, help="directorio de salida")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--smoke", action="store_true",
                    help="prueba rapida (3 semillas, N=20, G=10); NO es resultado")
    ap.add_argument("--suplementario", action="store_true",
                    help="experimento EXPLORATORIO: solo cambia G (por defecto 300, 40 semillas)")
    ap.add_argument("--G", type=int, default=None, help="solo con --suplementario")
    ap.add_argument("--n-semillas", type=int, default=None, help="solo con --suplementario")
    a = ap.parse_args(argv)
    cfg, semillas, directorio = configuracion(a)
    return correr_todo(directorio, cfg, semillas, workers=a.workers)


if __name__ == "__main__":
    raise SystemExit(principal())