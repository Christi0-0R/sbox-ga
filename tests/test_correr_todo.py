import json
import os
import sys
import types

import pandas as pd
import pytest

from experimentos import config
from experimentos import correr_todo as ct

CFG_MINI = dict(config.CFG, N=12, G=6)


@pytest.fixture
def aleatoria_falsa(monkeypatch):
    """Sustituye la busqueda aleatoria real por una minima (solo prueba la logica de correr_todo)."""
    mod = types.ModuleType("experimentos.baseline_aleatoria")

    def correr_aleatoria(semilla, cfg, ruta_csv):
        pd.DataFrame(dict(variante=["aleatoria"], semilla=[semilla])).to_csv(
            ruta_csv, index=False, lineterminator="\n")
        return None
    mod.correr_aleatoria = correr_aleatoria
    monkeypatch.setitem(sys.modules, "experimentos.baseline_aleatoria", mod)


def test_corre_todo_y_guarda_artefactos(tmp_path, aleatoria_falsa):
    d = str(tmp_path / "r")
    assert ct.correr_todo(d, CFG_MINI, [1000, 1001], workers=1) == 0
    for v in ct.VARIANTES:
        for s in (1000, 1001):
            assert os.path.exists(ct.ruta_csv(d, v, s))
    # S-box guardada para las variantes del AG, y consistente con su CSV
    for v in ("estatica", "adaptativa"):
        j = json.load(open(ct.ruta_sbox(d, v, 1000)))
        assert sorted(j["sbox"]) == list(range(256))
        ultimo = pd.read_csv(ct.ruta_csv(d, v, 1000)).iloc[-1]
        assert (j["nl"], j["delta"]) == (ultimo.nl_mejor, ultimo.delta_mejor)
        assert j["fitness"] == ultimo.fit_mejor
    assert os.path.exists(os.path.join(d, "meta.json"))
    assert not [n for n in os.listdir(d) if n.endswith(".tmp")]


def test_reanuda_sin_repetir(tmp_path, aleatoria_falsa):
    d = str(tmp_path / "r")
    ct.correr_todo(d, CFG_MINI, [1000], workers=1)
    ruta = ct.ruta_csv(d, "estatica", 1000)
    antes = os.path.getmtime(ruta)
    contenido = open(ruta).read()
    os.remove(ct.ruta_csv(d, "adaptativa", 1000))          # simula corrida perdida
    open(ruta + ".tmp", "w").write("basura a medias")      # y un .tmp huerfano
    assert ct.correr_todo(d, CFG_MINI, [1000], workers=1) == 0
    assert os.path.getmtime(ruta) == antes and open(ruta).read() == contenido
    assert os.path.exists(ct.ruta_csv(d, "adaptativa", 1000))
    assert not os.path.exists(ruta + ".tmp")


def test_reproducible_entre_ejecuciones(tmp_path, aleatoria_falsa):
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    ct.correr_todo(a, CFG_MINI, [1000], variantes=("estatica", "adaptativa"), workers=1)
    ct.correr_todo(b, CFG_MINI, [1000], variantes=("estatica", "adaptativa"), workers=1)
    for v in ("estatica", "adaptativa"):
        assert open(ct.ruta_csv(a, v, 1000)).read() == open(ct.ruta_csv(b, v, 1000)).read()


def test_paralelo_igual_a_secuencial(tmp_path, aleatoria_falsa):
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    ct.correr_todo(a, CFG_MINI, [1000, 1001], variantes=("estatica",), workers=1)
    ct.correr_todo(b, CFG_MINI, [1000, 1001], variantes=("estatica",), workers=2)
    for s in (1000, 1001):
        assert open(ct.ruta_csv(a, "estatica", s)).read() == open(ct.ruta_csv(b, "estatica", s)).read()


def test_no_mezcla_configuraciones(tmp_path, aleatoria_falsa):
    d = str(tmp_path / "r")
    ct.correr_todo(d, CFG_MINI, [1000], variantes=("estatica",), workers=1)
    with pytest.raises(SystemExit):
        ct.correr_todo(d, dict(CFG_MINI, mutpb=0.5), [1001], variantes=("estatica",), workers=1)


def test_config_py_coincide_con_la_congelada():
    # Si falla: config.py no tiene los valores calibrados (ventana=20, div_min=0.05, factor=2.0)
    assert config.CFG == ct.CFG_CONGELADA


def test_cada_variante_se_ejecuta_con_su_modo(tmp_path, monkeypatch, aleatoria_falsa):
    import src.motor_ga as motor
    llamadas = {}
    real = motor.correr

    def espia(semilla, adaptativo, cfg, ruta):
        llamadas[(semilla, ruta.split("/")[-1].split("_")[0])] = adaptativo
        return real(semilla, adaptativo, cfg, ruta)
    monkeypatch.setattr(motor, "correr", espia)
    ct.correr_todo(str(tmp_path / "r"), CFG_MINI, [1000], workers=1)
    assert llamadas[(1000, "estatica")] is False
    assert llamadas[(1000, "adaptativa")] is True