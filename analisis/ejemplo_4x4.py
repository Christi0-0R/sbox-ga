'''
Ejemplo didáctico: DDT de una S-box de 4 bits (la de PRESENT)
NO es la evaluación del proyecto
'''

S = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
n = len(S)

T = [[0] * n for _ in range(n)]
for dx in range(n):
    for x in range(n):
        T[dx][S[x] ^ S[x ^ dx]] += 1

print("DDT 4x4 (filas: dx, columnas: dy)")
for dx in range(n):
    print(f"{dx:2d} | " + " ".join(f"{v:2d}" for v in T[dx]))

print("delta =", max(max(fila) for fila in T[1:]))