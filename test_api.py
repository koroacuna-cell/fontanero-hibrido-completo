import requests

# Lista de pruebas
tests = [
    "mi ducha pierde agua",
    "la cisterna está goteando",
    "no enciende la caldera",
    "la lavadora no arranca",
    "hay agua fría en la ducha",
    "gotea el grifo del baño"
]

url = "http://127.0.0.1:5005/evaluar"

for t in tests:
    resp = requests.post(url, json={"texto": t})
    if resp.status_code == 200:
        data = resp.json()
        print(f"\n🧪 Consulta: {t}")
        print(f"➡️ Etiqueta: {data['etiqueta']}, Porcentaje: {data['porcentaje']}%")
        print("Coincidencias:")
        for frase, score in data['coincidencias']:
            print(f"  - {frase}: {score}")
    else:
        print(f"Error {resp.status_code}: {resp.text}")
