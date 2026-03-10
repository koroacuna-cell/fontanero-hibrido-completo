#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict
import os

# Archivo de entrada
input_file = "resumen_motor_ia_final.txt"

# Leer líneas
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

resumen_por_etiqueta = OrderedDict()
current_etiqueta = None

for line in lines:
    stripped = line.strip()
    if stripped.startswith("🔧"):
        current_etiqueta = stripped
        resumen_por_etiqueta[current_etiqueta] = []
    elif stripped.startswith("-") and current_etiqueta:
        # Ignorar líneas de separación
        if stripped != "- ------------------------------------------------":
            resumen_por_etiqueta[current_etiqueta].append(stripped)

# Crear carpeta para los archivos por etiqueta
output_dir = "por_etiqueta"
os.makedirs(output_dir, exist_ok=True)

# Guardar un archivo por etiqueta
for etiqueta, items in resumen_por_etiqueta.items():
    # Nombre de archivo seguro
    nombre_archivo = etiqueta.replace("🔧", "").strip().replace(" ", "_") + ".txt"
    path = os.path.join(output_dir, nombre_archivo)
    with open(path, "w", encoding="utf-8") as f:
        f.write(etiqueta + "\n")
        for item in items:
            f.write(item + "\n")
    print(f"Archivo generado: {path}")

print("\n✅ Todos los archivos por etiqueta han sido generados en la carpeta 'por_etiqueta'.")


