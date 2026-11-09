'''
Configuración compartida por ambas variantes
Los valores PROVISIONAL se congelan antes de las 60 corridas
'''

CFG = dict(
    N=30,            # tamaño de población (fijo por la hipótesis)
    G=50,            # generaciones (fijo por la hipótesis)
    cxpb=0.9,        # PROVISIONAL: prob. de cruce
    mutpb=0.2,       # PROVISIONAL: prob. de mutación base
    indpb=0.02,      # PROVISIONAL: prob. de intercambio por posición
    k=3,             # tamaño de torneo
    lam=2.0,         # PROVISIONAL: peso de delta en el fitness (R7)
    # --- solo variante adaptativa (se calibran con la 1ra vuelta) ---
    ventana=5,       # PLACEHOLDER: generaciones sin mejora = estancamiento
    div_min=0.5,     # PLACEHOLDER: umbral de diversidad
    factor=1.5,      # PLACEHOLDER: factor de ajuste de mutpb
    mutpb_max=0.8,   # PLACEHOLDER: tope de mutpb
)

SEMILLAS_FINALES = list(range(1000, 1030))   # 30 semillas, iguales en ambas variantes
SEMILLAS_PRELIM = list(range(1, 21))         # 20 semillas, solo para calibrar