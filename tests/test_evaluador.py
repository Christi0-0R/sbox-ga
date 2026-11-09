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


def test_metricas_y_fitness_de_son_consistentes():
    from src.evaluador import metricas, fitness_de
    p = list(range(256))
    random.Random(3).shuffle(p)
    n, d = metricas(p)
    assert (n, d) == (nl(p), delta(p))
    assert fitness(p) == fitness_de(n, d)
    assert fitness_de(112, 4) == 112.0
    assert fitness_de(98, 10, lam=2.0) == 86.0



def test_fuerza_del_ataque_en_aes():
    from src.evaluador import sesgo_lineal, prob_diferencial
    assert sesgo_lineal(112) == 2 ** -4        # 0.0625
    assert prob_diferencial(4) == 2 ** -6      # 0.015625


def test_sesgo_lineal_coincide_con_el_espectro_de_walsh():
    # Contraste independiente: el sesgo calculado desde NL debe igualar max|W| / 512
    import numpy as np
    from src.evaluador import sesgo_lineal, walsh
    for semilla in range(5):
        p = list(range(256))
        random.Random(semilla).shuffle(p)
        directo = np.abs(walsh(p)[:, 1:]).max() / 512
        assert sesgo_lineal(nl(p)) == directo
