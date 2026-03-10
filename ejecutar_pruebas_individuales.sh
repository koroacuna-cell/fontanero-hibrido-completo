#!/bin/bash
# Script para ejecutar todas las palabras clave del maestro_local.json

# Lista de palabras clave (copiada de maestro_local.json)
PALABRAS_CLAVE=(
"grifo goteando"
"grifo de lavabo gotea"
"grifo roto"
"el grifo gotea"
"grifo pierde agua"
"grifo con fuga"
"fuga grifo"
"grifo dripping"
"grifito goteando"
"grifo que gotea"

"ducha pierde agua"
"fuga en ducha"
"agua chorrea ducha"
"ducha con fuga"
"ducha gotea"
"ducha que pierde"
"ducha dripping"
"agua sale ducha"
"ducha se filtra"

"cisterna pierde agua"
"cisterna rota"
"bota agua cisterna"
"cisterna fuga"
"cisterna que gotea"
"inodoro pierde agua"
"cisterna dripping"

"caldera no enciende"
"mi caldera no arranca"
"la caldera no arranca"
"caldera apagada"
"caldera no prende"
"caldera falla"
"caldera off"

"lavadora no enciende"
"lavadora apagada"
"lavadora no funciona"
"mi lavadora no arranca"
"lavadora off"
"lavadora falla"

"tuberia rota"
"tuberia con fuga"
"tubo roto"
"cañería rota"
"tuberia quebrada"
"tubo fisurado"
"pipe broken"

"ducha fría"
"agua fría en ducha"
"ducha sin agua caliente"
"ducha no caliente"
"ducha fría agua"
"ducha cold"
"ducha sin calor"
)

echo "=== EJECUTANDO PRUEBAS AUTOMÁTICAS INDIVIDUALES ==="

for PROBLEMA in "${PALABRAS_CLAVE[@]}"; do
    echo ""
    echo "💡 Probando: $PROBLEMA"
    python3 pruebas_individuales.py <<< "$PROBLEMA"
done

echo ""
echo "=== FIN DE PRUEBAS AUTOMÁTICAS INDIVIDUALES ==="
