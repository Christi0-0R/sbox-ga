# calibracion.py

Explora la variante adaptativa para ver cómo se comporta con distintos umbrales.

resumen(nombre, cfg, adaptativo)

- Para cada semilla preliminar corre el AG y guarda el CSV en resultados/calib/.
- Lee el CSV y extrae: fitness, NL y δ finales (d.iloc[-1], última fila), y la diversidad y mutpb promedio desde la generación 10 (.iloc[10:]), para ignorar el arranque.
- Promedia sobre las 5 semillas e imprime una línea.

Rejilla:

- 2 controles estáticos: estatica_base (mutpb=0.2) y estatica_mutpb0.8. El segundo es el control clave: si la adaptativa se comporta igual que esta, la “adaptación” no aporta nada.
- 12 adaptativas: div_min ∈ {0.05, 0.1, 0.2, 0.5} × ventana ∈ {3, 5, 8}.
- Total 14 configuraciones, como dice tu bitácora.

Observación para tu documentación: el criterio que usaste (comparar contra una estática con mutpb alto) es muy sensato, porque separa “el efecto de adaptar” del “efecto de simplemente mutar más”. Y tu pendiente de “esfuerzo de calibración equivalente para la estática” está bien identificado: la adaptativa tuvo 12 configuraciones y la estática solo 2, lo cual podría favorecer a la adaptativa en la comparación final.