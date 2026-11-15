import csv
import json
import os
import sys

import pytest

from experimentos import cifrar_archivos as ca
from experimentos import generar_muestras as gm
from src.cifrado import cifrar, descifrar
from src.gf256 import aes_sbox


def _perm(desplazamiento):
    return [(x + desplazamiento) % 256 for x in range(256)]


def _guardar(d, variante, semilla, fitness, delta, sbox=None):
    os.makedirs(os.path.join(d, "sboxes"), exist_ok=True)
    j = dict(variante=variante, semilla=semilla, sbox=sbox or _perm(semilla % 255 + 1),
             nl=100, delta=delta, fitness=fitness)
    with open(os.path.join(d, "sboxes", f"{variante}_{semilla}.json"), "w") as f:
        json.dump(j, f)


# --- muestras ---
def test_muestras_deterministas_y_validas():
    a, b = gm.png_rgb(), gm.png_rgb()
    assert a == b and a[:8] == b"\x89PNG\r\n\x1a\n"
    e = gm.elf_minimo()
    assert e == gm.elf_minimo() and e[:4] == b"\x7fELF" and len(e) == 129
    assert gm.MUESTRAS["vacio.bin"]() == b""
    assert len(gm.TEXTO.encode("utf-8")) > 500


def test_generar_escribe_todas(tmp_path):
    rutas = gm.generar(str(tmp_path))
    assert sorted(os.path.basename(r) for r in rutas) == sorted(gm.MUESTRAS)
    assert os.path.getsize(tmp_path / "vacio.bin") == 0


# --- regla de la mejor S-box ---
def test_mejor_sbox_maximo_fitness(tmp_path):
    d = str(tmp_path)
    _guardar(d, "estatica", 1000, 90.0, 8)
    _guardar(d, "estatica", 1001, 92.0, 8)
    assert ca.mejor_sbox(d, "estatica")["semilla"] == 1001


def test_mejor_sbox_empate_menor_delta_y_luego_semilla(tmp_path):
    d = str(tmp_path)
    _guardar(d, "estatica", 1003, 92.0, 8)
    _guardar(d, "estatica", 1002, 92.0, 8)
    _guardar(d, "estatica", 1005, 92.0, 6)
    assert ca.mejor_sbox(d, "estatica")["semilla"] == 1005      # menor delta
    os.remove(os.path.join(d, "sboxes", "estatica_1005.json"))
    assert ca.mejor_sbox(d, "estatica")["semilla"] == 1002      # menor semilla


def test_mejor_sbox_no_mezcla_variantes(tmp_path):
    d = str(tmp_path)
    _guardar(d, "estatica", 1000, 80.0, 8)
    _guardar(d, "adaptativa", 1001, 99.0, 8)
    assert ca.mejor_sbox(d, "estatica")["semilla"] == 1000


def test_mejor_sbox_sin_datos(tmp_path):
    with pytest.raises(SystemExit):
        ca.mejor_sbox(str(tmp_path), "estatica")


# --- comparacion ---
def test_comparacion_recalcula_metricas_de_aes():
    filas = ca.tabla_comparacion([("aes", "", list(aes_sbox()))])
    f = filas[0]
    assert (f["nl"], f["delta"], f["fitness"]) == (112, 4, 112.0)
    assert f["sesgo_lineal"] == round(16 / 256, 4) and f["prob_diferencial"] == round(4 / 256, 4)


# --- ejecucion completa ---
@pytest.fixture
def entorno(tmp_path):
    final = str(tmp_path / "final")
    _guardar(final, "estatica", 1000, 92.0, 8)
    _guardar(final, "adaptativa", 1001, 92.0, 8)
    ej = str(tmp_path / "ej")
    gm.generar(ej)
    return final, ej, str(tmp_path / "sal")


def test_ejecucion_completa(entorno, monkeypatch):
    final, ej, sal = entorno
    monkeypatch.setattr(ca, "TAM_ALEATORIO", 5000)
    assert ca.principal(final, ej, sal) == 0
    filas = list(csv.DictReader(open(os.path.join(sal, "cifrado_archivos.csv"))))
    assert len(filas) == 3 * 5                                   # 3 S-box x 5 archivos
    assert all(f["coincide"] == "si" for f in filas)
    assert {f["archivo"] for f in filas} >= {"texto.txt", "imagen.png", "vacio.bin", "aleatorio_1MiB.bin"}
    vacio = [f for f in filas if f["archivo"] == "vacio.bin"]
    assert all(f["cifrado_distinto"] == "n/a" for f in vacio)
    otros = [f for f in filas if f["archivo"] != "vacio.bin"]
    assert all(f["cifrado_distinto"] == "si" for f in otros)
    assert os.path.exists(os.path.join(sal, "comparacion_sboxes.csv"))


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="el ELF solo corre en Linux")
def test_ejecutable_recuperado_se_ejecuta(entorno, monkeypatch):
    final, ej, sal = entorno
    monkeypatch.setattr(ca, "TAM_ALEATORIO", 100)
    ca.principal(final, ej, sal)
    filas = list(csv.DictReader(open(os.path.join(sal, "cifrado_archivos.csv"))))
    elf = [f for f in filas if f["archivo"] == ca.EJECUTABLE]
    assert elf and all(f["ejecuta_recuperado"] in ("si", "n/a") for f in elf)
    if sys.platform.startswith("linux"):
        assert all(f["ejecuta_recuperado"] == "si" for f in elf)


def test_detecta_descifrado_corrupto(entorno, monkeypatch):
    final, ej, sal = entorno
    monkeypatch.setattr(ca, "TAM_ALEATORIO", 100)

    def malo(ruta_in, ruta_out, sbox, bloque=1 << 20):
        with open(ruta_in, "rb") as f:
            datos = f.read()
        with open(ruta_out, "wb") as f:
            f.write(descifrar(datos, sbox)[:-1] + b"\x00" if datos else b"x")
    monkeypatch.setattr(ca, "descifrar_archivo", malo)
    assert ca.principal(final, ej, sal) > 0


def test_detecta_cifrado_que_no_cambia_nada(entorno, monkeypatch):
    final, ej, sal = entorno
    monkeypatch.setattr(ca, "TAM_ALEATORIO", 100)
    import shutil
    monkeypatch.setattr(ca, "cifrar_archivo", lambda i, o, s, bloque=1 << 20: shutil.copy(i, o))
    monkeypatch.setattr(ca, "descifrar_archivo", lambda i, o, s, bloque=1 << 20: shutil.copy(i, o))
    assert ca.principal(final, ej, sal) > 0       # coincide=si pero cifrado_distinto=NO


def test_sin_ejemplos_falla_claro(entorno, tmp_path):
    final, _, sal = entorno
    vacia = tmp_path / "nada"
    vacia.mkdir()
    with pytest.raises(SystemExit):
        ca.principal(final, str(vacia), sal)


# --- pruebas extra (cierran mutantes) ---
def test_fitness_de_la_comparacion_usa_lambda_2():
    from src.evaluador import metricas
    sb = _perm(1)
    nl_, d_ = (int(x) for x in metricas(sb))
    f = ca.tabla_comparacion([("x", 1, sb)])[0]
    assert d_ != 4 and f["fitness"] == nl_ - 2.0 * (d_ - 4)


def test_el_csv_marca_NO_si_el_hash_no_coincide(entorno, monkeypatch):
    final, ej, sal = entorno
    monkeypatch.setattr(ca, "TAM_ALEATORIO", 100)
    monkeypatch.setattr(ca, "descifrar_archivo",
                        lambda i, o, s, bloque=1 << 20: open(o, "wb").write(b"otra cosa"))
    assert ca.principal(final, ej, sal) > 0
    filas = list(csv.DictReader(open(os.path.join(sal, "cifrado_archivos.csv"))))
    assert all(f["coincide"] == "NO" for f in filas if f["bytes"] != "9")


def test_fallo_si_el_ejecutable_recuperado_no_ejecuta(entorno, monkeypatch):
    final, ej, sal = entorno
    monkeypatch.setattr(ca, "TAM_ALEATORIO", 100)
    monkeypatch.setattr(ca, "ejecuta_ok", lambda ruta: "no")
    assert ca.principal(final, ej, sal) == 3        # solo las 3 filas del ejecutable


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="usa un script de shell")
def test_ejecuta_ok_distingue_exito_y_error(tmp_path):
    ok, mal = tmp_path / "ok.sh", tmp_path / "mal.sh"
    ok.write_text("#!/bin/sh\nexit 0\n")
    mal.write_text("#!/bin/sh\nexit 3\n")
    assert ca.ejecuta_ok(str(ok)) == "si"
    assert ca.ejecuta_ok(str(mal)) == "no"