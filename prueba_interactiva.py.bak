import motor_inteligente
import json
import os

UMBRAL = 0.25  # Similitud mínima para considerar coincidencia
ARCHIVO_PENDIENTES = "preguntas_pendientes.json"

# Crear archivo de pendientes si no existe
if not os.path.exists(ARCHIVO_PENDIENTES):
    with open(ARCHIVO_PENDIENTES, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4, ensure_ascii=False)

print("=== PRUEBA INTERACTIVA AVANZADA ===")

while True:
    problema = input("\n💬 Describe tu problema (o 'salir'): ").strip()
    if problema.lower() == "salir":
        print("👋 Hasta luego!")
        break
    if not problema:
        print("⚠️ Escribe algo.")
        continue

    top3 = motor_inteligente.buscar_top3(problema)
    mejor_sim, mejor = top3[0]

    print("\n🔍 Mejor similitud encontrada:", f"{mejor_sim:.3f}")
    print("\n=== TOP 3 coincidencias ===")
    for sim, entrada in top3:
        print(f"✔️ {entrada['etiqueta']} — similitud: {sim:.3f}")

    print("\n=== RESPUESTA FINAL ===")
    if mejor_sim < UMBRAL:
        print("❌ No he encontrado una solución para eso. Envíame una foto 📸 por WhatsApp y te ayudaré.")
        # Guardar pregunta pendiente automáticamente sin duplicados
        with open(ARCHIVO_PENDIENTES, "r+", encoding="utf-8") as f:
            pendientes = json.load(f)
            if problema not in pendientes:
                pendientes.append(problema)
                f.seek(0)
                json.dump(pendientes, f, indent=4, ensure_ascii=False)
                f.truncate()
                print("⚠️ Pregunta registrada para futura revisión.")
    else:
        for r in mejor["respuesta"]:
            print("✔️", r)

    print("------------------------------")
