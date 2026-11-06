# config.py (parametros compartidos)

Un diccionario `CFG` que ambas variantes leen, para garantizar que solo difiera el lazo de control:

| Parámetro         | Qué es
| ---               | ---
| `N=30`, `G=50`    | población y generaciones (fijos por H1)
| `cxpb=0.9`	    | probabilidad de que una pareja de padres se crucen
| `mutpb=0.2`	    | probabilidad de que un individuo mute (base; en la adaptativa es el piso)
| `indpb=0.02`      | dentro de un individuo que muta, probabilidad de intercambiar cada posición (~5 de 256 posiciones)
| `k=3`	            | tamaño del torneo (presión de selección)
| `ventana`, `div_min`, `factor`, `mutpb_max` | solo adaptativa: cuántas generaciones sin mejora = estancamiento, umbral de diversidad, cuánto se multiplica mutpb, y su tope


`SEMILLAS_FINALES` (1000-1029) y `SEMILLAS_PRELIM` (1-5) están separadas a propósito: supuesto 5, para que la calibración no contamine la evidencia de H1.