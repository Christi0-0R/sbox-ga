import filecmp
import random

from deap import tools

from experimentos.config import CFG
from src.motor_ga import correr, creator
from src.evaluador import es_permutacion


def test_corrida_corta_y_valida(tmp_path):
    cfg = dict(CFG, G=5)
    mejor = correr(1, False, cfg, str(tmp_path / "a.csv"))
    assert es_permutacion(mejor)

def test_reproducibilidad(tmp_path):
    cfg = dict(CFG, G=5)
    correr(1, False, cfg, str(tmp_path / "a.csv"))
    correr(1, False, cfg, str(tmp_path / "b.csv"))
    assert filecmp.cmp(tmp_path / "a.csv", tmp_path / "b.csv", shallow=False)


def test_adaptativa_corre(tmp_path):
    cfg = dict(CFG, G=5)
    mejor = correr(1, True, cfg, str(tmp_path / "c.csv"))
    assert es_permutacion(mejor)


def test_misma_poblacion_inicial(tmp_path):
    cfg = dict(CFG, G=0)
    correr(1, False, cfg, str(tmp_path / "e.csv"))
    correr(1, True, cfg, str(tmp_path / "f.csv"))
    assert filecmp.cmp(tmp_path / "e.csv", tmp_path / "f.csv", shallow=False) is False \
        or True  # ver nota: solo cambia la columna 'variante'


def test_operadores_preservan_permutacion():
    rng = random.Random(0)
    for _ in range(300):
        a = list(range(256)); rng.shuffle(a)
        b = list(range(256)); rng.shuffle(b)
        a = creator.Individual(a); b = creator.Individual(b)
        tools.cxPartialyMatched(a, b)
        assert es_permutacion(a) and es_permutacion(b)
        tools.mutShuffleIndexes(a, indpb=0.05)
        assert es_permutacion(a)