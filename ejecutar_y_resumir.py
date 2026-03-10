# ejecutar_y_resumir.py (versión final de resumen limpio)

from match_problema_module import ejecutar_matching  # tu módulo de matching
import sys

archivo_problemas = sys.argv[1] if len(sys.argv) > 1 else "problema_test_completo.txt"

# Ejecutar el motor de coincidencias
resultados = ejecutar_matching(archivo_problemas)

# Crear un diccionario por etiqueta
resumen_dict = {}
for r in resultados:
    etiqueta = r["entry"]["etiqueta"]
    if etiqueta not in resumen_dict:
        resumen_dict[etiqueta] = []
    resumen_dict[etiqueta].append(r["reason"])

# Generar texto limpio
resumen = "=== RESUMEN DE COINCIDENCIAS POR ETIQUETA ===\n\n"
for etiqueta, coincidencias in resumen_dict.items():
    resumen += f"🔧 {etiqueta}\n"
    for c in coincidencias:
        resumen += f" - {c}\n"
    resumen += "-"*50 + "\n"

# Guardar en archivo
with open("resumen_motor_ia.txt", "w") as f:
    f.write(resumen)

# Mostrar en pantalla
print(resumen)
