'''
Ejemplo didáctico: DDT de una S-box de 4 bits (la de PRESENT).
NO es la evaluación del proyecto.

Fuente: Bogdanov et al. (2007), "PRESENT: An Ultra-Lightweight Block Cipher",
CHES 2007, LNCS 4727, pp. 450-466. https://doi.org/10.1007/978-3-540-74735-2_31

El artículo da la S-box (sección 3) pero no publica la DDT completa. Lo que sí
publica son los criterios de diseño de la sección 4.3, que se comprueban aquí:
  C1. Para todo dx != 0 y dy != 0: DDT[dx][dy] <= 4  (delta = 4; prob. máx. 2^-2, sección 5.1)
  C2. Si wt(dx) = wt(dy) = 1: DDT[dx][dy] = 0
  C3. Para todo a != 0 y b != 0: |W_b(a)| <= 8
  C4. Si wt(a) = wt(b) = 1: |W_b(a)| <= 4
      El artículo escribe "= ±4", pero la S-box publicada no lo cumple literalmente:
      los coeficientes que involucran el bit 0 valen 0. Ohkuma (2009, "Weak Keys of
      Reduced-Round PRESENT for Linear Cryptanalysis", SAC 2009, LNCS 5867, sec. 3.1)
      lo confirma: las máscaras de un bit no incluyen el bit 0 y su desviación
      absoluta es 2^-3 (|W| = 4). Lo que se cumple, y se comprueba, es |W| <= 4,
      equivalente al sesgo <= 2^-3 del apéndice del artículo.
'''

S = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
n = len(S)


def peso(v):
    return bin(v).count("1")


def ddt(s):
    t = [[0] * len(s) for _ in s]
    for dx in range(len(s)):
        for x in range(len(s)):
            t[dx][s[x] ^ s[x ^ dx]] += 1
    return t


def walsh(s):
    # W[b][a] = suma_x (-1)^(b·S(x) xor a·x)
    m = len(s)
    return [[sum(-1 if (peso(b & s[x]) + peso(a & x)) % 2 else 1 for x in range(m))
             for a in range(m)] for b in range(m)]


def criterios_present(s):
    t, w = ddt(s), walsh(s)
    m = len(s)
    nz = range(1, m)
    uno = [v for v in nz if peso(v) == 1]
    return {
        "C1_delta_max_4": max(t[dx][dy] for dx in nz for dy in nz) <= 4,
        "C2_un_bit_a_un_bit_es_0": all(t[dx][dy] == 0 for dx in uno for dy in uno),
        "C3_walsh_max_8": max(abs(w[b][a]) for a in nz for b in nz) <= 8,
        "C4_walsh_un_bit_max_4": all(abs(w[b][a]) <= 4 for a in uno for b in uno),
    }


if __name__ == "__main__":
    T = ddt(S)
    print("DDT 4x4 (filas: dx, columnas: dy)")
    for dx in range(n):
        print(f"{dx:2d} | " + " ".join(f"{v:2d}" for v in T[dx]))
    print("delta =", max(max(fila) for fila in T[1:]))
    print()
    print("Criterios de diseño de PRESENT (Bogdanov et al., 2007, sección 4.3):")
    for k, ok in criterios_present(S).items():
        print(f"  {k}: {'cumple' if ok else 'NO CUMPLE'}")
