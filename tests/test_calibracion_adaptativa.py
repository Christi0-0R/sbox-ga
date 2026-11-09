import pandas as pd

from experimentos import calibracion_adaptativa as ca


def _df(filas):
    # (ventana, div_min, factor, fit, explora)
    d = pd.DataFrame([dict(ventana=v, div_min=m, factor=f, fit=fit, nl=0, delta=0,
                           explora=ex, mutpb_medio=0) for v, m, f, fit, ex in filas])
    d["elegible"] = d.explora.between(ca.EXPLORA_MIN, ca.EXPLORA_MAX)
    return d


def test_compuerta_descarta_las_que_no_se_mueven_o_saturan():
    df = _df([(5, 0.05, 1.25, 95.0, 0.0),     # nunca explora
              (5, 0.15, 1.5, 94.0, 0.95),     # casi siempre explorando (aleatoria)
              (10, 0.15, 1.5, 88.0, 0.30)])
    e = ca.elegir(df)
    assert (e.ventana, e.div_min, e.factor) == (10, 0.15, 1.5)


def test_si_ninguna_pasa_la_compuerta_no_se_elige():
    df = _df([(5, 0.05, 1.25, 90.0, 0.0), (10, 0.15, 1.5, 91.0, 1.0)])
    assert ca.elegir(df) is None


def test_gana_el_mejor_si_no_hay_empate():
    df = _df([(5, 0.05, 2.0, 90.0, 0.3), (20, 0.30, 1.25, 88.0, 0.3)])
    assert ca.elegir(df).fit == 90.0


def test_en_empate_gana_la_mas_simple():
    # Empate (dentro de la tolerancia): factor menor, luego ventana mayor, luego div_min menor
    df = _df([(5, 0.15, 2.0, 88.0, 0.3), (10, 0.15, 1.25, 87.9, 0.3), (20, 0.15, 1.25, 87.8, 0.3)])
    e = ca.elegir(df)
    assert (e.ventana, e.factor) == (20, 1.25)


def test_tolerancia_es_estricta():
    df = _df([(5, 0.15, 2.0, 88.0, 0.3), (20, 0.15, 1.25, 87.6, 0.3)])   # diferencia 0.4
    assert ca.elegir(df).factor == 2.0