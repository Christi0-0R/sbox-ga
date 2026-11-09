import pandas as pd

from experimentos import calibracion_estatica as ce


def _df(filas):
    return pd.DataFrame([dict(mutpb=m, indpb=i, k=k, fit=f, nl=0, delta=0, div=0,
                              dist=ce._distancia(m, i, k)) for m, i, k, f in filas])


def test_distancia_base_es_cero():
    assert ce._distancia(*ce.BASE) == 0
    assert ce._distancia(0.4, 0.05, 5) == 3


def test_gana_el_mejor_si_no_hay_empate():
    df = _df([(0.1, 0.01, 2, 90.0), (0.2, 0.02, 3, 87.0), (0.4, 0.05, 5, 87.2)])
    e = ce.elegir(df)
    assert (e.mutpb, e.indpb, e.k) == (0.1, 0.01, 2)


def test_en_empate_gana_la_mas_cercana_a_la_base():
    df = _df([(0.4, 0.05, 5, 88.0), (0.2, 0.02, 3, 87.8), (0.1, 0.01, 2, 87.9)])
    e = ce.elegir(df)
    assert (e.mutpb, e.indpb, e.k) == (0.2, 0.02, 3)


def test_tolerancia_es_estricta():
    df = _df([(0.4, 0.05, 5, 88.0), (0.2, 0.02, 3, 87.6)])   # diferencia 0.4 > 0.3
    e = ce.elegir(df)
    assert (e.mutpb, e.indpb, e.k) == (0.4, 0.05, 5)