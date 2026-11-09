import numpy as np
import pandas as pd

from experimentos.config import CFG
from experimentos.baseline_aleatoria import flujo_aleatorio, correr_aleatoria
from src.motor_ga import correr
from src.evaluador import nl, delta, fitness

CFG_CHICA = dict(CFG, N=10, G=4)


def test_flujo_es_reproducible_y_consistente():
    f1, n1, d1 = flujo_aleatorio(3, 20, CFG["lam"])
    f2, n2, d2 = flujo_aleatorio(3, 20, CFG["lam"])
    assert (f1 == f2).all() and (n1 == n2).all() and (d1 == d2).all()
    assert (f1 == n1 - CFG["lam"] * (d1 - 4)).all()


def test_flujo_prefijo_estable():
    # Pedir más evaluaciones no cambia las primeras
    corto, _, _ = flujo_aleatorio(5, 10, CFG["lam"])
    largo, _, _ = flujo_aleatorio(5, 30, CFG["lam"])
    assert (corto == largo[:10]).all()


def test_esquema_y_presupuesto(tmp_path):
    ruta = tmp_path / "r.csv"
    correr_aleatoria(1, CFG_CHICA, str(ruta))
    d = pd.read_csv(ruta)
    assert len(d) == CFG_CHICA["G"] + 1
    assert list(d.generacion) == list(range(CFG_CHICA["G"] + 1))
    assert (d.variante == "aleatoria").all()
    assert not d.isna().any().any()
    assert (d.fit_mejor.diff().dropna() >= 0).all()
    assert (d.fit_mejor == d.nl_mejor - CFG["lam"] * (d.delta_mejor - 4)).all()


def test_mismo_punto_de_partida_que_el_ag(tmp_path):
    # Generación 0 de la aleatoria == generación 0 del AG (misma población inicial)
    cfg = dict(CFG_CHICA, G=0)
    correr_aleatoria(2, cfg, str(tmp_path / "r.csv"))
    correr(2, False, cfg, str(tmp_path / "e.csv"))
    r = pd.read_csv(tmp_path / "r.csv").drop(columns="variante")
    e = pd.read_csv(tmp_path / "e.csv")[list(r.columns) + ["variante"]].drop(columns="variante")
    pd.testing.assert_frame_equal(r, e)


def test_mejor_final_coincide_con_evaluador():
    # El fitness del flujo coincide con el evaluador oficial
    import random
    random.seed(4)
    perm = list(range(256)); random.shuffle(perm)
    f, n, d = flujo_aleatorio(4, 1, CFG["lam"])
    assert n[0] == nl(perm) and d[0] == delta(perm) and f[0] == fitness(perm)