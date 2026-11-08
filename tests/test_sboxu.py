import pytest
from src.gf256 import aes_sbox
from src.evaluador import nl, delta


def test_sboxu_coincide_en_aes():
    pytest.importorskip("sboxU")   # se salta si no hay Sage
    from src.verificacion import metricas_sboxu
    assert metricas_sboxu(aes_sbox()) == (nl(aes_sbox()), delta(aes_sbox())) == (112, 4)