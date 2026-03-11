#!/usr/bin/env python3
"""
VALIDADOR DE JSON - Fontanero Virtual PRO
Protege contra duplicados, formato incorrecto y corrupción de datos
"""

import json
import os
import sys
from datetime import datetime

def normalize_key(key):
    """Normaliza clave para detectar duplicados"""
    return key.lower().strip().replace(' ', '_').replace('-', '_')

def validate_entry(key, entry, existing_keys):
    """Valida una entrada individual"""
    errors = []
    warnings = []
    
    # Verificar que es un diccionario
    if not isinstance(entry, dict):
        errors.append(f"Entrada '{key}' no es un diccionario")
        return errors, warnings
    
    # Verificar campos requeridos
    if 'pasos' not in entry and 'steps' not in entry:
        errors.append(f"Entrada '{key}' no tiene 'pasos' o 'steps'")
    
    # Verificar que pasos es una lista
    pasos = entry.get('pasos') or entry.get('steps') or []
    if not isinstance(pasos, list):
        errors.append(f"Entrada '{key}': 'pasos' debe ser una lista")
    elif len(pasos) == 0:
        warnings.append(f"Entrada '{key}': 'pasos' está vacío")
    
    # Verificar alias (opcional pero recomendado)
    alias = entry.get('alias') or entry.get('aliases') or []
    if alias and not isinstance(alias, list):
        errors.append(f"Entrada '{key}': 'alias' debe ser una lista")
    
    # Verificar duplicados por clave normalizada
    normalized = normalize_key(key)
    if normalized in existing_keys:
        errors.append(f"Entrada '{key}' es duplicada de '{existing_keys[normalized]}'")
    
    # Verificar campos opcionales recomendados
    if 'pro' in entry and not isinstance(entry['pro'], bool):
        warnings.append(f"Entrada '{key}': 'pro' debería ser booleano")
    
    if 'source' in entry and entry['source'] not in ['internal', 'manufacturer', 'manual', 'experience', 'ia_generated', 'ia_reviewed', 'auto_generated']:
        warnings.append(f"Entrada '{key}': 'source' tiene valor no estándar: {entry['source']}")
    
    return errors, warnings

def validate_json_file(filepath, fix_duplicates=True):
    """Valida un archivo JSON completo"""
    print(f"\n🔍 Validando: {filepath}")
    print("=" * 70)
    
    if not os.path.exists(filepath):
        print(f"❌ Archivo no existe: {filepath}")
        return False, None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON corrupto: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Error al leer: {e}")
        return False, None
    
    if not isinstance(data, dict):
        print(f"❌ El JSON debe ser un diccionario, no {type(data)}")
        return False, None
    
    print(f"📊 Total entradas: {len(data)}")
    
    # Validar cada entrada
    all_errors = []
    all_warnings = []
    existing_keys = {}  # Para detectar duplicados
    cleaned_data = {}
    
    for key, entry in data.items():
        errors, warnings = validate_entry(key, entry, existing_keys)
        
        # Guardar clave normalizada para detectar duplicados
        normalized = normalize_key(key)
        if normalized in existing_keys:
            if fix_duplicates:
                print(f"⚠️  DUPLICADO DETECTADO: '{key}' ≡ '{existing_keys[normalized]}'")
                print(f"   → Manteniendo: '{existing_keys[normalized]}'")
                print(f"   → Descartando: '{key}'")
                continue  # Saltar duplicado
            else:
                errors.append(f"Duplicado detectado")
        
        existing_keys[normalized] = key
        
        all_errors.extend([(key, e) for e in errors])
        all_warnings.extend([(key, w) for w in warnings])
        
        # Añadir a datos limpios si no tiene errores críticos
        if not errors:
            cleaned_data[key] = entry
    
    # Mostrar resultados
    print(f"\n📋 RESULTADOS:")
    print(f"   ✅ Entradas válidas: {len(cleaned_data)}")
    print(f"   ⚠️  Advertencias: {len(all_warnings)}")
    print(f"   ❌ Errores: {len(all_errors)}")
    
    if all_warnings:
        print(f"\n⚠️  ADVERTENCIAS:")
        for key, warning in all_warnings[:10]:  # Mostrar solo primeras 10
            print(f"   • {key}: {warning}")
        if len(all_warnings) > 10:
            print(f"   ... y {len(all_warnings) - 10} más")
    
    if all_errors:
        print(f"\n❌ ERRORES:")
        for key, error in all_errors[:10]:  # Mostrar solo primeras 10
            print(f"   • {key}: {error}")
        if len(all_errors) > 10:
            print(f"   ... y {len(all_errors) - 10} más")
    
    # Guardar versión limpia si hubo cambios
    if len(cleaned_data) < len(data):
        backup_path = filepath + '.backup.' + datetime.now().strftime('%Y%m%d_%H%M%S')
        print(f"\n💾 Creando backup: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        if fix_duplicates:
            print(f"\n✅ Guardando versión limpia...")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            print(f"   → Eliminados {len(data) - len(cleaned_data)} duplicados/errores")
    
    # Resumen final
    print("\n" + "=" * 70)
    if all_errors:
        print("⚠️  VALIDACIÓN COMPLETADA CON ERRORES")
        return False, cleaned_data
    else:
        print("✅ VALIDACIÓN COMPLETADA SIN ERRORES")
        return True, cleaned_data

def add_entry_safely(filepath, key, entry, validate_first=True):
    """Añade una entrada de forma segura con validación"""
    print(f"\n🔒 Añadiendo entrada segura: '{key}'")
    
    # Cargar datos existentes
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}
    
    # Verificar duplicados
    normalized = normalize_key(key)
    existing_keys = {normalize_key(k): k for k in data.keys()}
    
    if normalized in existing_keys:
        print(f"❌ DUPLICADO: '{key}' ya existe como '{existing_keys[normalized]}'")
        return False
    
    # Validar entrada
    errors, warnings = validate_entry(key, entry, existing_keys)
    
    if errors:
        print(f"❌ ERRORES DE VALIDACIÓN:")
        for error in errors:
            print(f"   • {error}")
        return False
    
    if warnings:
        print(f"⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"   • {warning}")
        confirm = input("¿Continuar de todos modos? (s/n): ")
        if confirm.lower() != 's':
            return False
    
    # Añadir entrada
    data[key] = entry
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Entrada '{key}' añadida correctamente")
    return True

if __name__ == '__main__':
    # Uso: python3 validate_json.py [archivo.json]
    filepath = sys.argv[1] if len(sys.argv) > 1 else './json/responses.json'
    
    success, data = validate_json_file(filepath)
    
    if not success:
        print("\n⚠️  Se detectaron problemas. Revisa el archivo antes de continuar.")
        sys.exit(1)
    else:
        print("\n✅ JSON válido. Puedes continuar con confianza.")
        sys.exit(0)
