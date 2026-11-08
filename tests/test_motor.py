import random

import pandas as pd
import pytest
from deap import tools

from experimentos.config import CFG
from src.motor_ga import correr, creator, actualizar_parametros, _descendencia, _evaluar
from src.evaluador import es_permutacion, nl, delta, fitness_de

COLUMNAS = ["variante", "semilla", "generacion", "fit_mejor", "fit_max_pob", "fit_prom",
            "nl_mejor", "delta_mejor", "nl_prom", "delta_prom",
            "diversidad", "sin_mejora", "mutpb", "cxpb"]

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
            off = _descendencia(pop, cxpb, mutpb, CFG, lam)
            assert len(off) == len(pop)
            for ind in off:
                assert es_permutacion(ind)
                assert ind.fitness.valid
                assert ind.nl == nl(ind) and ind.delta == delta(ind)
                assert ind.fitness.values[0] == fitness_de(nl(ind), delta(ind), lam)


# ---------- control de parámetros

def test_estatica_no_cambia_parametros(tmp_path):
    _, d = _csv(tmp_path, "a.csv", 1, False, dict(CFG, G=15))
    assert (d.mutpb == CFG["mutpb"]).all()
    assert (d.cxpb == CFG["cxpb"]).all()


def test_adaptativa_respeta_limites(tmp_path):
    _, d = _csv(tmp_path, "a.csv", 1, True, dict(CFG, G=30))
    assert (d.mutpb >= CFG["mutpb"]).all()
    assert (d.mutpb <= CFG["mutpb_max"]).all()
    assert (d.cxpb == CFG["cxpb"]).all()


# Estas pruebas se reescriben en la Etapa 4 cuando cambie la regla de ajuste
def test_actualizar_parametros_sube_si_estancado():
    nuevo = actualizar_parametros(0.2, CFG["ventana"], 0.9, CFG)
    assert nuevo == pytest.approx(0.2 * CFG["factor"])


def test_actualizar_parametros_sube_si_poca_diversidad():
    nuevo = actualizar_parametros(0.2, 0, CFG["div_min"] / 2, CFG)
    assert nuevo > 0.2


def test_actualizar_parametros_no_pasa_el_tope():
    assert actualizar_parametros(CFG["mutpb_max"], 99, 0.0, CFG) == CFG["mutpb_max"]


def test_actualizar_parametros_relaja_hacia_la_base():
    assert actualizar_parametros(0.6, 0, 0.9, CFG) == pytest.approx(0.6 / CFG["factor"])
    assert actualizar_parametros(CFG["mutpb"], 0, 0.9, CFG) == CFG["mutpb"]


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