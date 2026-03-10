import json

# Cargar JSON limpio
with open("maestro_local_limpio.json", encoding="utf-8") as f:
    maestro = json.load(f)

# Leer problemas de prueba
with open("problema_test.txt", encoding="utf-8") as f:
    problemas = [line.strip() for line in f if line.strip()]

# Construir diccionario de sinónimos (etiqueta + sinónimos)
sinonimos_dict = {}
for entry in maestro:
    etiqueta_lower = entry["etiqueta"].lower()
    sinonimos_dict[etiqueta_lower] = entry
    for s in entry.get("sinonimos", []):
        sinonimos_dict[s.lower()] = entry

# Ejecutar pruebas individuales con coincidencia parcial
print("=== EJECUTANDO PRUEBAS INDIVIDUALES SYNONYMOUS ===\n")

for p in problemas:
    p_lower = p.lower()
    coincidencias = []
    for key, e in sinonimos_dict.items():
        if key in p_lower or p_lower in key:
            if e not in coincidencias:
                coincidencias.append((e, key))  # Guardamos entry y sinónimo que coincidió
    if coincidencias:
        for entry, sinco in coincidencias:
            print(f"🔧 Resultado para: {entry['etiqueta']} (coincidió con: '{sinco}')")
            for r in entry.get("respuesta", []):
                print(f"- {r}")
            print("-" * 50)
    else:
        print(f"❌ No he encontrado una solución para: {p}. Envía foto por WhatsApp 📸 y te ayudaré.")
        print("-" * 50)

print("=== FIN DE PRUEBAS INDIVIDUALES SYNONYMOUS ===")
