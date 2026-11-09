'''
Configuración compartida por ambas variantes
Todos los valores estan congelados (etapas 3 y 4) antes de las corridas finales
'''

CFG = dict(
    N=100,           # población (calibración etapa 3)
    G=100,           # generaciones (calibración etapa 3)
    cxpb=0.9,        # probabilidad de cruce
    mutpb=0.4,       # calibrado (etapa 3.5)
    indpb=0.02,      # calibrado (etapa 3.5)
    k=5,             # calibrado (etapa 3.5): tamaño de torneo
    lam=2.0,         # FIJO: decisión metodológica (R7)
    # --- solo variante adaptativa ---
    k_explorar=3,    # FIJO: k al explorar (decidido antes de calibrar)
    mutpb_max=0.8,   # FIJO: tope de mutpb (decidido antes de calibrar)
    indpb_max=0.1,   # FIJO: tope de indpb (decidido antes de calibrar)
    div_rec=0.6,     # FIJO: diversidad con la que se termina de explorar (decidido antes de calibrar)
    ventana=20,      # calibrado (etapa 4): generaciones sin mejora = estancamiento
    div_min=0.05,    # calibrado (etapa 4): diversidad por debajo de la cual se explora
    factor=2.0,      # calibrado (etapa 4): factor de ajuste
)

SEMILLAS_FINALES = list(range(1000, 1100))   # n = 100 por variante, iguales en ambas
SEMILLAS_PRELIM = list(range(1, 21))         # 20 semillas, solo para calibrar, nunca para el análisis final