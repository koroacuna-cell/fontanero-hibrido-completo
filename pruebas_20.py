from main import responder

preguntas = [
    "El grifo del lavabo está goteando",
    "La cisterna tarda mucho en llenarse",
    "La ducha sale fría",
    "El calentador no enciende",
    "La tubería del fregadero está atascada",
    "El agua caliente va y viene",
    "La caldera hace ruidos extraños",
    "El váter pierde agua por la base",
    "El grifo está muy duro",
    "No sale agua por la ducha",
    "La presión es muy baja en toda la casa",
    "Hay una fuga en la cocina",
    "La bomba de agua no arranca",
    "El lavamanos traga muy lento",
    "El agua sale con poca presión solo en la ducha",
    "El grifo no mezcla bien la temperatura",
    "El cartucho del grifo creo que está roto",
    "La caldera calienta demasiado y luego se apaga",
    "El bidé está goteando",
    "No sale agua caliente en el lavabo"
]

print("=== INICIO DE TEST CON 20 PREGUNTAS ===\n")

for i, pregunta in enumerate(preguntas, start=1):
    print(f"🔹 Pregunta {i}: {pregunta}")
    print(f"➡️ Respuesta: {responder(pregunta)}\n")

print("=== FIN DEL TEST ===")