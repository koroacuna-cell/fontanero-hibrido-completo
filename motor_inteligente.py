import json
import difflib

# Cargar datos del maestro
def cargar_maestro():
    with open("maestro_local.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Devuelve las 3 mejores coincidencias para un problema dado
def buscar_top3(problema_usuario):
    problema_usuario = problema_usuario.lower().strip()
    data = cargar_maestro()

    candidatos = []
    for entrada in data:
        etiqueta = entrada["etiqueta"]
        sinonimos = entrada.get("sinonimos", [])
        todos = [etiqueta] + sinonimos

        mejor_sim = 0
        for s in todos:
            sim = difflib.SequenceMatcher(None, problema_usuario.lower(), s.lower()).ratio()
            if sim > mejor_sim:
                mejor_sim = sim

        candidatos.append((mejor_sim, entrada))

    candidatos.sort(key=lambda x: x[0], reverse=True)
    return candidatos[:3]  # top 3

# Función para mostrar la respuesta final de forma interactiva
def resolver(problema_usuario):
    top3 = buscar_top3(problema_usuario)

    print("=== TOP 3 coincidencias ===")
    for sim, entrada in top3:
        print(f"✔️ {entrada['etiqueta']} — similitud: {sim:.3f}")

    mejor_sim, mejor = top3[0]

    print("\n=== RESPUESTA FINAL ===")
    if mejor_sim < 0.25:
        print("❌ No he encontrado una solución para eso. Envíame una foto 📸 por WhatsApp y te ayudo.")
    else:
        for r in mejor["respuesta"]:
            print("✔️", r)

    print("------------------------------")
