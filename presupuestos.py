#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Presupuestos Estimativos - Fontanero Eduardo Quiroz
Precios orientativos para Torrevieja (Alicante) - IVA no incluido
"""

# Tabla de precios base (rango mínimo-máximo) +20% sobre estándar
PRECIOS_BASE = {
    # GRIFERÍA
    'grifo': (40, 65),
    'grifo_gotea': (45, 70),
    'grifo_no_cierra': (45, 70),
    'grifo_bloqueado': (40, 60),
    'grifo_sin_presion': (35, 55),
    
    # CISTERNAS E INODOROS
    'cisterna': (60, 140),  # Rango amplio según tu indicación
    'cisterna_gotea': (60, 120),
    'cisterna_no_cierra': (60, 130),
    'cisterna_pierde_agua': (70, 140),
    'inodoro': (60, 130),
    
    # TERMOS Y AGUA CALIENTE
    'termo': (60, 100),
    'termo_no_calienta': (70, 120),
    'termo_gotea': (60, 110),
    'termo_fuga_agua': (80, 150),
    'calentador': (70, 130),
    'calentador_no_enciende': (80, 140),
    
    # DESAGÜES Y ATASCOS
    'desague': (50, 90),
    'desague_lento': (45, 75),
    'desague_atascado': (60, 100),
    'atasco_cocina': (70, 120),
    'atasco_bano': (60, 110),
    'fregadero_atascado': (55, 95),
    
    # TUBERÍAS Y FUGAS
    'fuga': (70, 150),
    'fuga_agua': (80, 160),
    'tuberia_goteando': (60, 130),
    'tuberia_rota': (90, 200),
    'fuga_oculta': (100, 250),  # Requiere detección
    
    # CALEFACCIÓN
    'calefaccion': (60, 110),
    'radiador': (40, 70),  # por unidad
    'radiador_frio': (45, 75),
    'calefaccion_no_calienta': (70, 130),
    
    # CALDERAS
    'caldera': (80, 180),
    'caldera_no_enciende': (90, 200),
    'filtro_caldera_sucio': (50, 85),
    
    # OTROS
    'lavabo': (50, 90),
    'ducha': (45, 80),
    'ducha_sin_presion': (40, 70),
    'bañera': (60, 120),
    'lavadora_pierde_agua': (55, 95),
    'lavavajillas_pierde_agua': (60, 100),
    
    # SERVICIOS GENERALES
    'visita_diagnostico': (35, 50),
    'urgencia': None,  # Se calcula como recargo
    'materiales': None,  # Se añade según caso
}

# Recargos
RECARGO_URGENCIA = 1.25  # +25% mismo día
RECARGO_FINDE = 1.30     # +30% fin de semana/festivo
MATERIALES_BASICOS = (15, 35)  # Rango materiales estándar

def obtener_rango(problema_clave):
    """Devuelve el rango de precio para un problema dado."""
    # Normalizar clave
    clave = problema_clave.lower().strip().replace(' ', '_')
    
    # Buscar match exacto
    if clave in PRECIOS_BASE and PRECIOS_BASE[clave]:
        return PRECIOS_BASE[clave]
    
    # Buscar por contención (si "grifo" está en la clave)
    for key, rango in PRECIOS_BASE.items():
        if key in clave or clave in key:
            if rango:
                return rango
    
    # Default si no encuentra
    return (50, 100)  # Precio por defecto

def calcular_presupuesto(problema_clave, urgencia=False, finde=False, materiales=False, complejidad='media'):
    """
    Calcula presupuesto estimativo.
    
    Args:
        problema_clave: Clave del problema (ej: 'cisterna_gotea')
        urgencia: bool - ¿Es urgencia mismo día?
        finde: bool - ¿Fin de semana/festivo?
        materiales: bool - ¿Incluir materiales básicos?
        complejidad: 'baja' | 'media' | 'alta' - Ajusta dentro del rango
    
    Returns:
        str: Presupuesto formateado (ej: "60-140€ estimado")
    """
    min_base, max_base = obtener_rango(problema_clave)
    
    # Ajustar por complejidad
    if complejidad == 'baja':
        factor = 0.8
    elif complejidad == 'alta':
        factor = 1.2
    else:  # media
        factor = 1.0
    
    min_ajustado = min_base * factor
    max_ajustado = max_base * factor
    
    # Aplicar recargos
    if urgencia:
        min_ajustado *= RECARGO_URGENCIA
        max_ajustado *= RECARGO_URGENCIA
    
    if finde:
        min_ajustado *= RECARGO_FINDE
        max_ajustado *= RECARGO_FINDE
    
    # Añadir materiales si aplica
    if materiales:
        min_ajustado += MATERIALES_BASICOS[0]
        max_ajustado += MATERIALES_BASICOS[1]
    
    # Redondear a múltiplos de 5
    min_final = round(min_ajustado / 5) * 5
    max_final = round(max_ajustado / 5) * 5
    
    return f"{int(min_final)}-{int(max_final)}€ estimado"

def generar_respuesta_con_presupuesto(problema_clave, pasos, urgencia=False, finde=False):
    """Genera respuesta completa con solución + presupuesto."""
    presupuesto = calcular_presupuesto(problema_clave, urgencia=urgencia, finde=finde)
    
    respuesta = " | ".join(pasos) if pasos else ""
    
    return f"{respuesta} | 💰 Presupuesto orientativo: {presupuesto} (IVA no incluido). Para valoración exacta, envíame foto por WhatsApp 📸"

# Test rápido
if __name__ == "__main__":
    print("🧪 TEST DE PRESUPUESTOS")
    print("-" * 40)
    
    test_cases = [
        ('grifo_gotea', False, False),
        ('cisterna_gotea', False, False),
        ('cisterna_pierde_agua', True, False),  # urgencia
        ('termo_no_calienta', False, True),     # finde
        ('fuga_oculta', True, True),            # urgencia + finde
    ]
    
    for problema, urg, fin in test_cases:
        resultado = calcular_presupuesto(problema, urgencia=urg, finde=fin)
        print(f"{problema:<25} → {resultado}")
