import random, time
from src.evaluador import fitness

p = list(range(256))
random.shuffle(p)
fitness(p)  # calentamiento

t = time.time()
for _ in range(200):
    fitness(p)
dt = (time.time() - t) / 200
print(f"{dt*1000:.2f} ms por evaluación")
print(f"90,000 evaluaciones: {dt*90000/60:.1f} minutos")