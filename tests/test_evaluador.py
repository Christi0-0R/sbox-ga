import random
from src.gf256 import aes_sbox
from src.evaluador import nl, delta, es_permutacion, ddt, fitness
from src.verificacion import delta_directo, nl_fwht


def test_regresion_aes():
    s = aes_sbox()
    assert nl(s) == 112
    assert delta(s) == 4


def test_identidad_es_lineal():
    s = list(range(256))
    assert nl(s) == 0
    assert delta(s) == 256


def test_ddt_filas_suman_256():
    p = list(range(256))
    random.Random(1).shuffle(p)
    T = ddt(p)
    assert (T.sum(axis=1) == 256).all()
    assert T[0, 0] == 256 and T[0].sum() == 256


def test_contraste_independiente_en_aes():
    s = aes_sbox()
    assert nl_fwht(s) == nl(s) == 112
    assert delta_directo(s) == delta(s) == 4


def test_contraste_independiente_en_aleatorias():
    rng = random.Random(2026)
    for _ in range(10):
        p = list(range(256))
        rng.shuffle(p)
        assert es_permutacion(p)
        assert nl(p) == nl_fwht(p)
        assert delta(p) == delta_directo(p)


def test_fitness_aes():
    assert fitness(aes_sbox()) == 112.0