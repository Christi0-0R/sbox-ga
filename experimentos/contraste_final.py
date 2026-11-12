"""
Contrasta las S-boxes FINALES de cada corrida del AG (resultados/<dir>/sboxes/*.json):
recalcula NL, delta y fitness con tres implementaciones y los compara con lo guardado.
  1) src/evaluador.py (el que uso el AG)
  2) src/verificacion.py (FWHT y conteo directo, independiente)
  3) sboxU (solo si hay Sage; si no, se omite y se avisa)

Uso:  python -m experimentos.contraste_final [directorio]   (por defecto resultados/final)
"""
import glob
import json
import os
import sys

from src.evaluador import metricas
from src.verificacion import delta_directo, nl_fwht


def _sboxu():
    try:
        from src.verificacion import metricas_sboxu
        from src.gf256 import aes_sbox
        metricas_sboxu(aes_sbox())
        return metricas_sboxu
    except Exception as e:
        print(f"sboxU no disponible ({type(e).__name__}): solo contraste interno")
        return None


def contrastar(directorio, lam=2.0):
    rutas = sorted(glob.glob(os.path.join(directorio, "sboxes", "*.json")))
    if not rutas:
        raise SystemExit(f"no hay JSON en {directorio}/sboxes")
    ext = _sboxu()
    fallos = []
    for r in rutas:
        j = json.load(open(r, encoding="utf-8"))
        s = j["sbox"]
        nombre = os.path.basename(r)
        if sorted(s) != list(range(256)):
            fallos.append((nombre, "no es permutacion"))
            continue
        guardado = (j["nl"], j["delta"])
        calculos = {"evaluador": tuple(int(x) for x in metricas(s)),
                    "verificacion": (int(nl_fwht(s)), int(delta_directo(s)))}
        if ext is not None:
            calculos["sboxU"] = tuple(int(x) for x in ext(s))
        for quien, val in calculos.items():
            if val != guardado:
                fallos.append((nombre, f"{quien}={val} guardado={guardado}"))
        fit = guardado[0] - lam * (guardado[1] - 4)
        if abs(fit - j["fitness"]) > 1e-9:
            fallos.append((nombre, f"fitness guardado={j['fitness']} recalculado={fit}"))
    print(f"{len(rutas) - len({n for n, _ in fallos})}/{len(rutas)} S-boxes coinciden "
          f"({'con sboxU' if ext else 'sin sboxU'})")
    for n, m in fallos:
        print("DISCREPANCIA", n, m)
    return len(fallos)


if __name__ == "__main__":
    raise SystemExit(contrastar(sys.argv[1] if len(sys.argv) > 1 else "resultados/final"))