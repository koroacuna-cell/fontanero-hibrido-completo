from fontanero_virtual import buscar_solucion

# Lista de problemas a probar
problemas = [
    "grifo goteando",
    "ducha pierde agua",
    "caldera no enciende",
    "lavadora atascada",
    "cisterna pierde agua",
    "tubería rota",
    "grifo de lavabo gotea",
    "ducha fría"
]

print("=== EJECUTANDO TODAS LAS PRUEBAS AUTOMÁTICAS ===\n")

for problema in problemas:
    print(f"💬 Describe tu problema: {problema}\n")
    if not buscar_solucion(problema):
        print("❌ No he encontrado una solución para eso. Envía foto por WhatsApp 📸 y te ayudaré.")
    print("-" * 60)

print("\n=== FIN DE TODAS LAS PRUEBAS AUTOMÁTICAS ===")
