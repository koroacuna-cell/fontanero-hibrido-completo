import getpass
import motor_inteligente

# Diccionario de usuarios y contraseñas
credenciales = {
    "Administrador": "admin123",
    "Usuario": "usuario123"
}

print("=== PRUEBA INTERACTIVA GETPASS ===")

# Login
while True:
    usuario = input().strip()
    contrasena = getpass.getpass().strip()
    
    if credenciales.get(usuario) == contrasena:
        print(f"✅ Bienvenido, {usuario}!")
        break
    else:
        print("❌ Usuario o contraseña incorrectos. Intenta de nuevo.\n")

# Bucle interactivo
while True:
    problema = input("\n💬 Describe tu problema (o 'salir'): ").strip()
    if problema.lower() == "salir":
        print("👋 Sesión finalizada. Hasta luego!")
        break
    if not problema:
        print("⚠️ Escribe algo.")
        continue
    
    # Mostrar top 3 coincidencias
    top3 = motor_inteligente.buscar_top3(problema)
    print("\n=== TOP 3 coincidencias ===")
    for sim, entrada in top3:
        print(f"✔️ {entrada['etiqueta']} — similitud: {sim:.3f}")
    
    # Mostrar respuesta final
    mejor_sim, mejor = top3[0]
    print("\n=== RESPUESTA FINAL ===")
    if mejor_sim < 0.25:
        print("❌ No he encontrado una solución para eso. Envíame una foto 📸 por WhatsApp y te ayudo.")
    else:
        for r in mejor["respuesta"]:
            print("✔️", r)
    print("------------------------------")
