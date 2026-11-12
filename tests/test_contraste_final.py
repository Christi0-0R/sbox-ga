import json
import os
import random

import pytest

from experimentos.contraste_final import contrastar
from src.evaluador import metricas
from src.gf256 import aes_sbox


def _guardar(d, nombre, s, **cambios):
    nl_, de_ = metricas(s)
    j = dict(variante="estatica", semilla=1, sbox=list(s), nl=int(nl_), delta=int(de_),
             fitness=float(nl_ - 2.0 * (de_ - 4)))
    j.update(cambios)
    os.makedirs(os.path.join(d, "sboxes"), exist_ok=True)
    json.dump(j, open(os.path.join(d, "sboxes", nombre), "w"))


def _perm(sem):
    p = list(range(256))
    random.Random(sem).shuffle(p)
    return p


def test_sboxes_correctas_coinciden(tmp_path):
    _guardar(str(tmp_path), "a.json", aes_sbox())
    _guardar(str(tmp_path), "b.json", _perm(1))
    assert contrastar(str(tmp_path)) == 0


@pytest.mark.parametrize("cambio", [dict(nl=1), dict(delta=99), dict(fitness=0.0)])
def test_detecta_valores_guardados_incorrectos(tmp_path, cambio):
    _guardar(str(tmp_path), "a.json", _perm(2), **cambio)
    assert contrastar(str(tmp_path)) > 0


def test_detecta_sbox_que_no_es_permutacion(tmp_path):
    _guardar(str(tmp_path), "a.json", _perm(3), sbox=[0] * 256)
    assert contrastar(str(tmp_path)) > 0


def test_directorio_vacio_falla(tmp_path):
    with pytest.raises(SystemExit):
        contrastar(str(tmp_path))


@pytest.mark.parametrize("que", ["nl_fwht", "delta_directo", "metricas"])
def test_cada_implementacion_cuenta(tmp_path, monkeypatch, que):
    # S-box correcta; si UNA implementacion discrepa, debe detectarse
    import experimentos.contraste_final as cf
    _guardar(str(tmp_path), "a.json", _perm(4))
    assert cf.contrastar(str(tmp_path)) == 0
    real = getattr(cf, que)
    if que == "metricas":
        monkeypatch.setattr(cf, que, lambda s: (real(s)[0] + 2, real(s)[1]))
    else:
        monkeypatch.setattr(cf, que, lambda s: real(s) + 2)
    assert cf.contrastar(str(tmp_path)) > 0


def test_mensaje_de_permutacion(tmp_path, capsys):
    _guardar(str(tmp_path), "a.json", _perm(3), sbox=[0] * 256)
    contrastar(str(tmp_path))
    assert "no es permutacion" in capsys.readouterr().out