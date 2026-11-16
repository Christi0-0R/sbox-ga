"""El ejemplo 4x4 (S-box de PRESENT) cumple los criterios publicados por
Bogdanov et al. (2007, sección 4.3), y la verificación detecta S-boxes que no."""
from analisis.ejemplo_4x4 import S, ddt, walsh, criterios_present


def test_sbox_present_es_permutacion():
    assert sorted(S) == list(range(16))


def test_present_cumple_criterios_del_articulo():
    assert all(criterios_present(S).values())


def test_delta_present_es_4():
    t = ddt(S)
    assert max(max(f) for f in t[1:]) == 4


def test_ddt_filas_suman_16():
    assert all(sum(f) == 16 for f in ddt(S))


def test_walsh_fila_cero_es_trivial():
    w = walsh(S)
    assert w[0][0] == 16 and all(v == 0 for v in w[0][1:])


def test_identidad_no_cumple():
    # La identidad es lineal: delta = 16 y Walsh = ±16, falla C1 a C4.
    c = criterios_present(list(range(16)))
    assert not any(c.values())


def test_walsh_un_bit_coincide_con_ohkuma_2009():
    # Máscaras de un bit: |W| es 0 o 4, y ninguna con |W| = 4 toca el bit 0.
    w = walsh(S)
    for a in (1, 2, 4, 8):
        for b in (1, 2, 4, 8):
            assert abs(w[b][a]) in (0, 4)
            if abs(w[b][a]) == 4:
                assert 1 not in (a, b)
