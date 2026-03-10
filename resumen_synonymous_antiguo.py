import json
import sys

# Cargar maestro limpio
with open("maestro_local_limpio.json", encoding="utf-8") as f:
    maestro = json.load(f)

# Elegir archivo de problemas (por defecto problema_test_completo.txt)
archivo_problemas = sys.argv[1] if len(sys.argv) > 1 else "problema_test_completo.txt"
with open(archivo_problemas, encoding="utf-8") as f:
    problemas = [line.strip() for line in f if line.strip()]

# Construir diccionario de sinónimos (etiqueta + sinónimos)
sinonimos_dict = {}
for entry in maestro:
    etiqueta_lower = entry["etiqueta"].lower()
    sinonimos_dict[etiqueta_lower] = entry
    for s in entry.get("sinonimos", []):
        sinonimos_dict[s.lower()] = entry

# Generar resumen único
resumen = {}
for p in problemas:
    p_lower = p.lower()
    for key, entry in sinonimos_dict.items():
        if key in p_lower or p_lower in key:
            etiqueta = entry["etiqueta"]
            if etiqueta not in resumen:
                resumen[etiqueta] = set()
            resumen[etiqueta].add(p)
            break

# Mostrar resumen
print("=== RESUMEN DE COINCIDENCIAS POR ETIQUETA ===\n")
for etiqueta, coincidencias in resumen.items():
    print(f"🔧 {etiqueta}")
    for c in sorted(coincidencias):
        print(f" - {c}")
    print("-" * 50)

print("=== FIN DEL RESUMEN ===")
