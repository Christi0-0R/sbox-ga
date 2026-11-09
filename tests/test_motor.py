import random

import pandas as pd
import pytest
from deap import tools

from experimentos.config import CFG
from src.motor_ga import correr, creator, actualizar_parametros, explorando, _descendencia, _evaluar
from src.evaluador import es_permutacion, nl, delta, fitness_de

COLUMNAS = ["variante", "semilla", "generacion", "fit_mejor", "fit_max_pob", "fit_prom",
            "nl_mejor", "delta_mejor", "nl_max_pob", "delta_min_pob", "nl_prom", "delta_prom",
            "diversidad", "sin_mejora", "sin_mejora_nl", "sin_mejora_delta",
            "mutpb", "indpb", "k", "cxpb"]

CFG_CORTA = dict(CFG, G=5)


def _csv(tmp_path, nombre, semilla, adaptativo, cfg=CFG_CORTA):
    ruta = tmp_path / nombre
    mejor = correr(semilla, adaptativo, cfg, str(ruta))
    return mejor, pd.read_csv(ruta)


# ---------- validez y reproducibilidad

@pytest.mark.parametrize("adaptativo", [False, True])
def test_corrida_corta_y_valida(tmp_path, adaptativo):
    mejor, _ = _csv(tmp_path, "a.csv", 1, adaptativo)
    assert es_permutacion(mejor)


@pytest.mark.parametrize("adaptativo", [False, True])
def test_reproducibilidad(tmp_path, adaptativo):
    _csv(tmp_path, "a.csv", 1, adaptativo)
    _csv(tmp_path, "b.csv", 1, adaptativo)
    assert (tmp_path / "a.csv").read_bytes() == (tmp_path / "b.csv").read_bytes()


def test_semillas_distintas_dan_corridas_distintas(tmp_path):
    _, a = _csv(tmp_path, "a.csv", 1, False)
    _, b = _csv(tmp_path, "b.csv", 2, False)
    assert not a.fit_prom.equals(b.fit_prom)


# ---------- comparabilidad entre variantes

def test_misma_poblacion_inicial(tmp_path):
    cfg = dict(CFG, G=0)
    _, e = _csv(tmp_path, "e.csv", 1, False, cfg)
    _, f = _csv(tmp_path, "f.csv", 1, True, cfg)
    assert e.variante[0] == "estatica" and f.variante[0] == "adaptativa"
    pd.testing.assert_frame_equal(e.drop(columns="variante"),
                                  f.drop(columns="variante"))


def test_poblaciones_iniciales_distintas_con_semillas_distintas(tmp_path):
    # Garantiza que el test anterior no sea vacuo: detecta diferencias reales
    cfg = dict(CFG, G=0)
    _, e = _csv(tmp_path, "e.csv", 1, False, cfg)
    _, f = _csv(tmp_path, "f.csv", 2, True, cfg)
    assert not e.drop(columns=["variante", "semilla"]).equals(
        f.drop(columns=["variante", "semilla"]))


# ---------- esquema y consistencia del CSV

@pytest.mark.parametrize("adaptativo", [False, True])
def test_esquema_csv(tmp_path, adaptativo):
    _, d = _csv(tmp_path, "a.csv", 7, adaptativo)
    assert list(d.columns) == COLUMNAS
    assert len(d) == CFG_CORTA["G"] + 1
    assert list(d.generacion) == list(range(CFG_CORTA["G"] + 1))
    assert not d.isna().any().any()
    assert (d.semilla == 7).all()
    assert (d.variante == ("adaptativa" if adaptativo else "estatica")).all()
    assert d.diversidad.between(0, 1).all()


@pytest.mark.parametrize("adaptativo", [False, True])
def test_fitness_consistente_con_nl_y_delta(tmp_path, adaptativo):
    _, d = _csv(tmp_path, "a.csv", 3, adaptativo)
    esperado = d.nl_mejor - CFG["lam"] * (d.delta_mejor - 4)
    assert (d.fit_mejor == esperado).all()


@pytest.mark.parametrize("adaptativo", [False, True])
def test_metricas_del_mejor_coinciden_con_evaluador(tmp_path, adaptativo):
    mejor, d = _csv(tmp_path, "a.csv", 4, adaptativo)
    assert mejor.nl == nl(mejor) and mejor.delta == delta(mejor)
    assert d.nl_mejor.iloc[-1] == nl(mejor)
    assert d.delta_mejor.iloc[-1] == delta(mejor)


@pytest.mark.parametrize("adaptativo", [False, True])
def test_elitismo_el_mejor_siempre_sigue_en_la_poblacion(tmp_path, adaptativo):
    # fit_mejor viene del Hall of Fame (monótono por construcción);
    # fit_max_pob viene de la población: solo coinciden si el elitismo funciona
    _, d = _csv(tmp_path, "a.csv", 5, adaptativo, dict(CFG, G=30))
    assert (d.fit_max_pob == d.fit_mejor).all()
    assert (d.fit_mejor.diff().dropna() >= 0).all()


def test_descendencia_tiene_metricas_y_fitness_vigentes():
    # Propiedad: todo individuo producido por cruce/mutación es permutación válida
    # y su NL, delta y fitness corresponden a su contenido ACTUAL
    random.seed(11)
    lam = CFG["lam"]
    pop = []
    for _ in range(10):
        p = list(range(256)); random.shuffle(p)
        ind = creator.Individual(p)
        _evaluar(ind, lam)
        pop.append(ind)
    for cxpb, mutpb in [(1.0, 1.0), (0.9, 0.2), (0.0, 1.0), (1.0, 0.0)]:
        for _ in range(3):
            off = _descendencia(pop, cxpb, mutpb, CFG["indpb"], CFG["k"], lam)
            assert len(off) == len(pop)
            for ind in off:
                assert es_permutacion(ind)
                assert ind.fitness.valid
                assert ind.nl == nl(ind) and ind.delta == delta(ind)
                assert ind.fitness.values[0] == fitness_de(nl(ind), delta(ind), lam)


# ---------- control de parámetros

BASE = dict(mutpb=CFG["mutpb"], indpb=CFG["indpb"], k=CFG["k"])
EXPL = dict(mutpb=CFG["mutpb"] * CFG["factor"], indpb=CFG["indpb"] * CFG["factor"],
            k=CFG["k_explorar"])
VENT = CFG["ventana"]
# Indicadores: (sin_mejora_nl, sin_mejora_delta, diversidad)
ESTANCADA = dict(sin_mejora_nl=VENT, sin_mejora_delta=VENT, div=0.9)
MOVIENDOSE = dict(sin_mejora_nl=0, sin_mejora_delta=0, div=0.9)


def test_estatica_no_cambia_parametros(tmp_path):
    _, d = _csv(tmp_path, "a.csv", 1, False, dict(CFG, G=15))
    for col in ("mutpb", "indpb", "k", "cxpb"):
        assert (d[col] == CFG[col]).all()


def test_adaptativa_respeta_limites(tmp_path):
    cfg = dict(CFG, G=30, N=30, div_min=0.99)   # fuerza exploración
    _, d = _csv(tmp_path, "a.csv", 1, True, cfg)
    assert (d.mutpb >= CFG["mutpb"]).all() and (d.mutpb <= CFG["mutpb_max"]).all()
    assert (d.indpb >= CFG["indpb"]).all() and (d.indpb <= CFG["indpb_max"]).all()
    assert set(d.k) <= {CFG["k"], CFG["k_explorar"]}
    assert (d.cxpb == CFG["cxpb"]).all()


def test_adaptativa_con_control_neutro_es_identica_a_la_estatica(tmp_path):
    # Prueba clave: con factor=1 y k_explorar=k el lazo de control no cambia nada,
    # asi que la ÚNICA diferencia entre variantes es el control de parámetros
    cfg = dict(CFG, N=30, G=20, factor=1.0, k_explorar=CFG["k"], div_min=0.99)
    _, e = _csv(tmp_path, "e.csv", 3, False, cfg)
    _, a = _csv(tmp_path, "a.csv", 3, True, cfg)
    pd.testing.assert_frame_equal(e.drop(columns="variante"), a.drop(columns="variante"))


def test_adaptativa_real_si_se_distingue_de_la_estatica(tmp_path):
    # Evita que la prueba anterior sea vacua: con control activo los parámetros sí cambian
    cfg = dict(CFG, N=30, G=20, div_min=0.99)
    _, e = _csv(tmp_path, "e.csv", 3, False, cfg)
    _, a = _csv(tmp_path, "a.csv", 3, True, cfg)
    assert (a.k != CFG["k"]).any() and (a.mutpb > CFG["mutpb"]).any()
    assert (e.k == CFG["k"]).all()


def _contadores_desde_csv(d):
    # Recalcula los contadores desde las columnas del CSV (variante estática: sin reinicios)
    mejor_nl, mejor_d = d.nl_max_pob[0], d.delta_min_pob[0]
    cnt_nl, cnt_d, esperado = 0, 0, [(0, 0)]
    mejoro_nl = mejoro_d = False
    for g in range(1, len(d)):
        if d.nl_max_pob[g] > mejor_nl:
            mejor_nl, cnt_nl, mejoro_nl = d.nl_max_pob[g], 0, True
        else:
            cnt_nl += 1
        if d.delta_min_pob[g] < mejor_d:
            mejor_d, cnt_d, mejoro_d = d.delta_min_pob[g], 0, True
        else:
            cnt_d += 1
        esperado.append((cnt_nl, cnt_d))
    return esperado, mejoro_nl, mejoro_d


def test_indicadores_nl_y_delta_miden_generaciones_sin_mejora(tmp_path):
    # Varias semillas para ver tanto mejoras como estancamientos de NL y de delta
    vio_nl = vio_d = False
    for semilla in (2, 7):   # en la semilla 7 mejora también delta
        _, d = _csv(tmp_path, f"a{semilla}.csv", semilla, False, dict(CFG, N=30, G=40))
        esperado, mejoro_nl, mejoro_d = _contadores_desde_csv(d)
        assert list(zip(d.sin_mejora_nl, d.sin_mejora_delta)) == esperado
        vio_nl |= mejoro_nl; vio_d |= mejoro_d
    assert vio_nl and vio_d   # el test no es vacuo: hubo mejoras de ambas métricas


def test_al_salir_de_explorar_el_estancamiento_se_mide_desde_cero(tmp_path):
    cfg = dict(CFG, N=30, G=60, div_min=0.99)
    _, d = _csv(tmp_path, "a.csv", 1, True, cfg)
    salidas = d.index[(d.k.shift(1) == CFG["k_explorar"]) & (d.k == CFG["k"])]
    assert len(salidas) > 0
    # Una generación después de reiniciar, el contador vale a lo sumo 1
    assert (d.sin_mejora_nl[salidas] <= 1).all()
    assert (d.sin_mejora_delta[salidas] <= 1).all()


def test_regla_estancada_explora():
    assert actualizar_parametros(BASE, ESTANCADA, CFG) == pytest.approx(EXPL)


def test_regla_poca_diversidad_explora():
    ind = dict(MOVIENDOSE, div=CFG["div_min"] / 2)
    assert actualizar_parametros(BASE, ind, CFG) == pytest.approx(EXPL)


def test_regla_solo_nl_estancado_no_basta():
    ind = dict(sin_mejora_nl=VENT, sin_mejora_delta=0, div=0.9)
    assert actualizar_parametros(BASE, ind, CFG) == BASE


def test_regla_sin_estancamiento_conserva_la_base():
    assert actualizar_parametros(BASE, MOVIENDOSE, CFG) == BASE


def test_regla_respeta_los_topes():
    p = dict(mutpb=CFG["mutpb_max"], indpb=CFG["indpb_max"], k=CFG["k_explorar"])
    for _ in range(5):
        p = actualizar_parametros(p, dict(MOVIENDOSE, div=0.0), CFG)
    assert p == dict(mutpb=CFG["mutpb_max"], indpb=CFG["indpb_max"], k=CFG["k_explorar"])


def test_regla_sigue_explorando_si_la_diversidad_no_se_recupera():
    p = actualizar_parametros(BASE, ESTANCADA, CFG)
    assert explorando(p, CFG)
    p2 = actualizar_parametros(p, dict(MOVIENDOSE, div=CFG["div_rec"] / 2), CFG)
    assert explorando(p2, CFG) and p2["mutpb"] >= p["mutpb"]


def test_regla_vuelve_a_la_base_al_recuperar_diversidad():
    # Histéresis: aunque siga "estancada", si la diversidad se recuperó se vuelve a explotar
    p = actualizar_parametros(BASE, ESTANCADA, CFG)
    ind = dict(ESTANCADA, div=CFG["div_rec"])
    assert actualizar_parametros(p, ind, CFG) == BASE


def test_regla_no_modifica_sus_argumentos():
    p = dict(BASE); ind = dict(ESTANCADA)
    actualizar_parametros(p, ind, CFG)
    assert p == BASE and ind == ESTANCADA


def test_adaptativa_no_se_queda_atorada_explorando(tmp_path):
    # Con la regla anterior, tras explorar una vez nunca volvía a explotar
    _, d = _csv(tmp_path, "a.csv", 1, True, dict(CFG, N=30, G=60, div_min=0.99))
    en_expl = (d.k == CFG["k_explorar"])
    assert en_expl.any() and (~en_expl).iloc[10:].any()


# ---------- operadores

def test_operadores_preservan_permutacion():
    rng = random.Random(0)
    for _ in range(300):
        a = list(range(256)); rng.shuffle(a)
        b = list(range(256)); rng.shuffle(b)
        a = creator.Individual(a); b = creator.Individual(b)
        tools.cxPartialyMatched(a, b)
        assert es_permutacion(a) and es_permutacion(b)
        tools.mutShuffleIndexes(a, indpb=0.05)
        assert es_permutacion(a)