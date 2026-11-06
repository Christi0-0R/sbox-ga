import time
from experimentos.config import CFG, SEMILLAS_PRELIM
from src.motor_ga import correr

for s in SEMILLAS_PRELIM:
    t = time.time()
    mejor = correr(s, False, CFG, f"resultados/prelim/estatica_{s}.csv")
    print(f"semilla {s}: {time.time() - t:.1f} s")