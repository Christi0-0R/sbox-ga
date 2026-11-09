import numpy as np
import pandas as pd
import pytest

from analisis import estadistica as est
from experimentos.config import CFG
from src.motor_ga import correr


def _serie(valores):
    return pd.Series(valores, index=range(len(valores)), dtype=float)


# ---------- piezas estadísticas

def test_holm_ejemplo_conocido():
    # p ordenados 0.01, 0.03, 0.04 -> 0.03, 0.06, 0.06 (monótonos, tope 1)
    aj = est.holm([0.01, 0.04, 0.03])
    assert aj == pytest.approx([0.03, 0.06, 0.06])
    assert est.holm([0.6, 0.9, 0.8]).max() <= 1.0


def test_cliff_extremos():
    assert est.cliff(np.array([5, 6, 7.]), np.array([1, 2, 3.])) == 1.0
    assert est.cliff(np.array([1, 2, 3.]), np.array([5, 6, 7.])) == -1.0
    assert est.cliff(np.array([1, 2, 3.]), np.array([1, 2, 3.])) == 0.0


def test_comparar_detecta_mejora_en_el_sentido_correcto():
    rng = np.random.default_rng(1)
    b = _serie(rng.normal(80, 1, 40))
    a = _serie(b.to_numpy() + 3 + rng.normal(0, 0.5, 40))      # a claramente mayor
    mayor = est.comparar(a, b, "mayor")
    menor = est.comparar(a, b, "menor")
    assert mayor["p_mw"] < 0.001 and mayor["p_wilcoxon"] < 0.001
    assert menor["p_mw"] > 0.99 and menor["p_wilcoxon"] > 0.99   # mismos datos, sentido contrario
    assert mayor["cliff"] > 0.9 and menor["cliff"] < -0.9         # efecto orientado a "a mejor"


def test_comparar_sin_diferencia():
    rng = np.random.default_rng(2)
    base = rng.normal(80, 1, 40)
    a, b = _serie(base), _serie(base)
    r = est.comparar(a, b, "mayor")
    assert r["dif"] == 0 and r["p_wilcoxon"] == 1.0 and r["p_mw"] > 0.4
    assert r["ic_inf"] == r["ic_sup"] == 0


def test_comparar_ic_contiene_la_diferencia_y_es_reproducible():
    rng = np.random.default_rng(3)
    b = _serie(rng.normal(80, 1, 60))
    a = _serie(b.to_numpy() + 2.0 + rng.normal(0, 0.3, 60))
    r1, r2 = est.comparar(a, b, "mayor"), est.comparar(a, b, "mayor")
    assert r1 == r2
    assert r1["ic_inf"] < 2.0 < r1["ic_sup"] and r1["dif"] == pytest.approx(2.0, abs=0.2)


def test_comparar_exige_las_mismas_semillas():
    a = pd.Series([1., 2, 3], index=[1, 2, 3])
    b = pd.Series([1., 2, 3], index=[1, 2, 4])
    with pytest.raises(ValueError):
        est.comparar(a, b, "mayor")


def test_tabla_comparacion_aplica_holm():
    rng = np.random.default_rng(4)
    n = 30
    base = rng.normal(80, 1, n)
    ra = pd.DataFrame(dict(nl_mejor=base + 2, delta_mejor=base, fit_mejor=base + 1.0), index=range(n))
    rb = pd.DataFrame(dict(nl_mejor=base, delta_mejor=base, fit_mejor=base), index=range(n))
    t = est.tabla_comparacion(ra, rb, est.PRINCIPALES)
    assert set(t.index) == {"nl_mejor", "delta_mejor", "fit_mejor"}
    assert (t.p_holm >= t.p_mw - 1e-12).all()
    assert t.loc["nl_mejor", "sentido"] == "mayor" and t.loc["delta_mejor", "sentido"] == "menor"


# ---------- mecanismo con datos armados a mano

def _corrida(semilla, fit, k):
    n = len(fit)
    return pd.DataFrame(dict(semilla=semilla, generacion=range(n), fit_mejor=fit, k=k),
                        index=range(n))


def test_mecanismo_calcula_la_ganancia_tras_cada_entrada():
    # La adaptativa entra a explorar en la generación 3 (k pasa de 5 a 3); ventana de 4 gens
    fit_a = [80, 80, 80, 80, 82, 82, 84, 84, 84, 84]
    fit_e = [80, 80, 80, 80, 80, 80, 82, 82, 82, 82]
    a = _corrida(1, fit_a, [5, 5, 5, 3, 3, 3, 5, 5, 5, 5])
    e = _corrida(1, fit_e, [5] * 10)
    m = est.mecanismo({1: a}, {1: e}, ventana=4)
    # entrada en g=3: ganancia adaptativa = fit_a[7]-fit_a[3] = 4; estática = fit_e[7]-fit_e[3] = 2
    assert m["eventos"] == 1
    assert m["ganancia_adaptativa"] == 4 and m["ganancia_estatica"] == 2
    assert m["frac_adaptativa_mayor"] == 1.0 and m["frac_estatica_mayor"] == 0.0


def test_mecanismo_ignora_entradas_sin_ventana_completa():
    a = _corrida(1, [80] * 6, [5, 5, 5, 5, 3, 3])           # entra en g=4, no caben 4 gens
    e = _corrida(1, [80] * 6, [5] * 6)
    assert est.mecanismo({1: a}, {1: e}, ventana=4)["eventos"] == 0


# ---------- de punta a punta con corridas reales pequeñas

@pytest.fixture(scope="module")
def directorio(tmp_path_factory):
    d = tmp_path_factory.mktemp("final")
    cfg = dict(CFG, N=30, G=20, div_min=0.99)      # fuerza modo explorar para tener eventos
    for s in range(1, 7):
        correr(s, False, cfg, str(d / f"estatica_{s}.csv"))
        correr(s, True, cfg, str(d / f"adaptativa_{s}.csv"))
        (d / f"aleatoria_{s}.csv").write_text((d / f"estatica_{s}.csv").read_text())  # sustituto
    return d


def test_resumen_corridas(directorio):
    r = est.resumen_corridas(est.cargar_corridas(str(directorio), "adaptativa"))
    assert list(r.index) == [1, 2, 3, 4, 5, 6]
    assert (r.sesgo_lineal == (128 - r.nl_mejor) / 256).all()
    assert (r.frac_explora > 0).all()


def test_analizar_de_punta_a_punta(directorio):
    out = est.analizar(str(directorio))
    assert set(out["principal"].index) == {"nl_mejor", "delta_mejor", "fit_mejor"}
    assert set(out["secundarias"].index) == {"auc_fit", "nl_prom_final", "delta_prom_final"}
    assert out["mecanismo"]["eventos"] > 0
    assert set(out["vs_aleatoria"].index.get_level_values(0)) == {"adaptativa", "estatica"}
    assert set(out["descriptiva"].variante) == {"estatica", "adaptativa", "aleatoria"}


def test_graficas_y_salida_a_disco(directorio, tmp_path):
    out = est.analizar(str(directorio))
    est.graficas(out["corridas"], str(tmp_path))
    for m in ("fit_mejor", "nl_mejor", "delta_mejor"):
        assert (tmp_path / f"convergencia_{m}.png").stat().st_size > 1000


def test_falla_claro_si_faltan_corridas(tmp_path):
    with pytest.raises(FileNotFoundError):
        est.analizar(str(tmp_path))