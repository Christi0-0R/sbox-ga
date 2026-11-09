"""
Contrasta el evaluador propio con verificacion.py y con sboxU (si hay Sage).
"""

import random
from src.gf256 import aes_sbox
from src.evaluador import nl, delta
from src.verificacion import delta_directo, nl_fwht


def sboxes_prueba(n=50, semilla=0):
    rng = random.Random(semilla)
    out = [aes_sbox()]
    for _ in range(n):
        p = list(range(256))
        rng.shuffle(p)
        out.append(p)
    return out


def main():
    try:
        from src.verificacion import metricas_sboxu
        metricas_sboxu(aes_sbox())
        hay_sboxu = True
    except Exception as e:
        print(f"sboxU no disponible ({type(e).__name__}); solo contraste interno")
        hay_sboxu = False

    fallos = 0
    for i, s in enumerate(sboxes_prueba()):
        propio = (nl(s), delta(s))
        interno = (nl_fwht(s), delta_directo(s))
        ok = propio == interno
        if hay_sboxu:
            ext = metricas_sboxu(s)
            ok = ok and propio == ext
        if not ok:
            fallos += 1
            print(f"DISCREPANCIA en S-box {i}: propio={propio} interno={interno}"
                  + (f" sboxU={ext}" if hay_sboxu else ""))
    total = len(sboxes_prueba())
    print(f"{total - fallos}/{total} coinciden"
          f" ({'con sboxU' if hay_sboxu else 'sin sboxU'})")
    return fallos


if __name__ == "__main__":
    raise SystemExit(main())