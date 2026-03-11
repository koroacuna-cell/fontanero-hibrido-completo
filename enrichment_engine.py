#!/usr/bin/env python3
"""
MOTOR DE ENRIQUECIMIENTO SEGURO - Fontanero Virtual PRO
Genera, valida e importa preguntas técnicas SIN corromper el JSON principal
"""

import json
import os
import sys
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

# Configuración
MAIN_JSON = './json/responses.json'
QUEUE_DIR = './queue'
APPROVED_DIR = './approved'
REVIEWED_DIR = './reviewed'
BACKUP_DIR = './backups'
MAX_JSON_SIZE_MB = 5  # Alerta si el JSON principal supera este tamaño

def normalize_key(key):
    """Normaliza clave para detectar duplicados de forma consistente"""
    return key.lower().strip().replace(' ', '_').replace('-', '_').replace('é', 'e').replace('ó', 'o').replace('á', 'a').replace('í', 'i').replace('ú', 'u')

def calculate_checksum(filepath):
    """Calcula checksum para detectar cambios"""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def create_backup(filepath):
    """Crea backup con timestamp y checksum"""
    if not os.path.exists(filepath):
        return None
    
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    checksum = calculate_checksum(filepath)[:8]
    backup_path = os.path.join(BACKUP_DIR, f'{Path(filepath).stem}_{timestamp}_{checksum}.json')
    
    shutil.copy2(filepath, backup_path)
    print(f"💾 Backup creado: {backup_path}")
    return backup_path

def validate_entry_structure(key, entry):
    """Valida estructura básica de una entrada"""
    errors = []
    
    if not isinstance(entry, dict):
        errors.append(f"'{key}' no es un diccionario")
        return errors
    
    # Campos requeridos
    if 'pasos' not in entry and 'steps' not in entry:
        errors.append(f"'{key}' falta 'pasos' o 'steps'")
    
    pasos = entry.get('pasos') or entry.get('steps')
    if pasos and not isinstance(pasos, list):
        errors.append(f"'{key}': 'pasos' debe ser lista")
    
    # Campos opcionales con validación de tipo
    if 'alias' in entry and not isinstance(entry['alias'], list):
        errors.append(f"'{key}': 'alias' debe ser lista")
    
    if 'pro' in entry and not isinstance(entry['pro'], bool):
        errors.append(f"'{key}': 'pro' debe ser booleano")
    
    if 'source' in entry and entry['source'] not in ['internal', 'manufacturer', 'manual', 'experience', 'ia_reviewed', 'auto_generated']:
        errors.append(f"'{key}': 'source' tiene valor no estándar: {entry['source']}")
    
    return errors

def validate_queue_file(filepath):
    """Valida un archivo de la cola antes de procesar"""
    print(f"🔍 Validando queue: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON corrupto en queue: {e}")
        return False, None, f"JSON corrupto: {e}"
    
    if not isinstance(data, dict) or len(data) != 1:
        return False, None, "Archivo de queue debe tener exactamente 1 entrada"
    
    key = list(data.keys())[0]
    entry = data[key]
    
    errors = validate_entry_structure(key, entry)
    if errors:
        return False, None, "; ".join(errors)
    
    return True, {key: entry}, None

def load_main_json():
    """Carga el JSON principal con validación"""
    if not os.path.exists(MAIN_JSON):
        return {}
    
    with open(MAIN_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_main_json(data):
    """Guarda el JSON principal con validación final"""
    # Validar antes de guardar
    for key, entry in data.items():
        errors = validate_entry_structure(key, entry)
        if errors:
            raise ValueError(f"Entrada inválida '{key}': {'; '.join(errors)}")
    
    # Verificar tamaño
    size_mb = len(json.dumps(data, ensure_ascii=False).encode('utf-8')) / (1024 * 1024)
    if size_mb > MAX_JSON_SIZE_MB:
        print(f"⚠️  ALERTA: JSON principal pesa {size_mb:.2f}MB (límite: {MAX_JSON_SIZE_MB}MB)")
        print("   Considera dividir en archivos por categoría")
    
    with open(MAIN_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON principal guardado ({size_mb:.2f}MB)")

def generate_question(topic, brand=None, error_code=None):
    """Genera una pregunta técnica para enriquecimiento"""
    from datetime import datetime
    
    # Plantillas de preguntas por categoría
    templates = {
        'caldera_error': {
            'question': f'¿Qué significa el código {error_code or "E9"} en caldera {brand or "Junkers"}?',
            'suggested_key': f'{brand.lower()}_{error_code.lower()}' if brand and error_code else None,
            'category': 'technical',
            'pro': True,
            'source': 'auto_generated'
        },
        'producto_precio': {
            'question': f'¿Cuánto cuesta un {topic}?',
            'suggested_key': f'{topic.lower()}_producto',
            'category': 'product',
            'pro': False,
            'source': 'auto_generated'
        },
        'reparacion_paso': {
            'question': f'¿Cómo se repara {topic}?',
            'suggested_key': f'{topic.lower()}_reparacion',
            'category': 'repair',
            'pro': False,
            'source': 'auto_generated'
        },
        'material_lista': {
            'question': f'¿Qué materiales necesito para instalar {topic}?',
            'suggested_key': f'{topic.lower()}_materiales',
            'category': 'materials',
            'pro': False,
            'source': 'auto_generated'
        }
    }
    
    # Seleccionar plantilla aleatoria o por categoría
    import random
    template_type = random.choice(list(templates.keys()))
    template = templates[template_type]
    
    return {
        'question': template['question'],
        'suggested_key': template['suggested_key'],
        'category': template['category'],
        'pro': template['pro'],
        'source': template['source'],
        'generated_at': datetime.now().isoformat(),
        'status': 'pending'
    }

def add_to_queue(question_data):
    """Añade una pregunta generada a la cola"""
    os.makedirs(QUEUE_DIR, exist_ok=True)
    
    # Verificar duplicados en queue
    key = question_data.get('suggested_key') or normalize_key(question_data['question'])
    normalized = normalize_key(key)
    
    # Cargar JSON principal para verificar duplicados globales
    main_data = load_main_json()
    existing_keys = {normalize_key(k): k for k in main_data.keys()}
    
    if normalized in existing_keys:
        print(f"⚠️  Saltando: '{key}' ya existe en JSON principal como '{existing_keys[normalized]}'")
        return False
    
    # Verificar duplicados en queue
    for filename in os.listdir(QUEUE_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(QUEUE_DIR, filename), 'r', encoding='utf-8') as f:
                try:
                    queue_data = json.load(f)
                    queue_key = list(queue_data.keys())[0]
                    if normalize_key(queue_key) == normalized:
                        print(f"⚠️  Saltando: '{key}' ya está en queue")
                        return False
                except:
                    continue
    
    # Crear archivo de queue
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    counter = len([f for f in os.listdir(QUEUE_DIR) if f.endswith('.json')]) + 1
    filename = f'{counter:04d}_{normalized}_{timestamp}.json'
    filepath = os.path.join(QUEUE_DIR, filename)
    
    entry = {
        key: {
            'alias': [question_data['question']],
            'pasos': ['[PENDIENTE DE GENERAR CON IA]'],
            'pro': question_data.get('pro', False),
            'source': question_data.get('source', 'auto_generated'),
            'category': question_data.get('category', 'general'),
            'generated_at': question_data.get('generated_at'),
            'status': 'pending'
        }
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Añadido a queue: {filename}")
    return True

def process_queue():
    """Procesa archivos de queue: valida y mueve a approved"""
    os.makedirs(APPROVED_DIR, exist_ok=True)
    
    processed = 0
    rejected = 0
    
    for filename in sorted(os.listdir(QUEUE_DIR)):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(QUEUE_DIR, filename)
        valid, data, error = validate_queue_file(filepath)
        
        if valid and data:
            # Mover a approved
            approved_path = os.path.join(APPROVED_DIR, filename)
            shutil.move(filepath, approved_path)
            print(f"✅ Aprobado: {filename}")
            processed += 1
        else:
            print(f"❌ Rechazado: {filename} - {error}")
            rejected += 1
            # Mover a rejected/ o eliminar
            os.remove(filepath)
    
    print(f"\n📊 Queue procesada: {processed} aprobados, {rejected} rechazados")
    return processed, rejected

def import_approved_to_main(dry_run=False):
    """Importa archivos aprobados al JSON principal con validación final"""
    if not os.listdir(APPROVED_DIR):
        print("✅ No hay archivos aprobados para importar")
        return 0
    
    # Cargar JSON principal
    main_data = load_main_json()
    existing_keys = {normalize_key(k): k for k in main_data.keys()}
    
    imported = 0
    skipped = 0
    errors = 0
    
    for filename in sorted(os.listdir(APPROVED_DIR)):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(APPROVED_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                entry_data = json.load(f)
            
            key = list(entry_data.keys())[0]
            entry = entry_data[key]
            normalized = normalize_key(key)
            
            # Verificar duplicado final
            if normalized in existing_keys:
                print(f"⚠️  Saltando duplicado: '{key}' ≡ '{existing_keys[normalized]}'")
                skipped += 1
                continue
            
            # Validación final de estructura
            struct_errors = validate_entry_structure(key, entry)
            if struct_errors:
                print(f"❌ Error de estructura en '{key}': {'; '.join(struct_errors)}")
                errors += 1
                continue
            
            # Añadir al JSON principal (en memoria primero)
            if not dry_run:
                main_data[key] = entry
                existing_keys[normalized] = key
            
            imported += 1
            print(f"✅ Listo para importar: {key}")
            
        except Exception as e:
            print(f"❌ Error procesando {filename}: {e}")
            errors += 1
    
    if dry_run:
        print(f"\n🔍 DRY RUN: {imported} entradas listas, {skipped} duplicadas, {errors} con errores")
        return imported
    
    # Si no es dry_run y hay entradas para importar
    if imported > 0 and not dry_run:
        # Backup antes de modificar
        backup = create_backup(MAIN_JSON)
        
        try:
            save_main_json(main_data)
            print(f"✅ {imported} entradas importadas al JSON principal")
            
            # Mover archivos importados a reviewed/
            os.makedirs(REVIEWED_DIR, exist_ok=True)
            for filename in os.listdir(APPROVED_DIR):
                if filename.endswith('.json'):
                    shutil.move(
                        os.path.join(APPROVED_DIR, filename),
                        os.path.join(REVIEWED_DIR, filename)
                    )
            
            return imported
            
        except Exception as e:
            print(f"❌ Error guardando JSON principal: {e}")
            if backup:
                print(f"🔄 Restaurando desde backup...")
                shutil.copy2(backup, MAIN_JSON)
                print("✅ Rollback completado")
            return -1
    
    return imported

def generate_batch(topics=None, brands=None, error_codes=None, count=10):
    """Genera un lote de preguntas para enriquecimiento"""
    import random
    
    if topics is None:
        topics = ['termo', 'grifo', 'cisterna', 'caldera', 'solar', 'aerotermia', 'aire acondicionado']
    if brands is None:
        brands = ['Junkers', 'Ariston', 'Saunier', 'Baxi', 'Roca', 'Gala']
    if error_codes is None:
        error_codes = ['EA', 'E9', 'F7', 'CE', '101', '103', '501', 'A01']
    
    generated = 0
    for _ in range(count):
        # Seleccionar tipo de pregunta aleatorio
        question_type = random.choice(['caldera_error', 'producto_precio', 'reparacion_paso', 'material_lista'])
        
        if question_type == 'caldera_error':
            brand = random.choice(brands) if brands else 'Junkers'
            error_code = random.choice(error_codes) if error_codes else 'E9'
            question = generate_question(
                topic=random.choice(topics) if topics else 'caldera',
                brand=brand,
                error_code=error_code
            )
        else:
            question = generate_question(topic=random.choice(topics))
        
        if add_to_queue(question):
            generated += 1
    
    print(f"\n✅ Generadas {generated} preguntas para enriquecimiento")
    return generated

def show_status():
    """Muestra estado del sistema de enriquecimiento"""
    print("\n" + "=" * 70)
    print("📊 ESTADO DEL MOTOR DE ENRIQUECIMIENTO")
    print("=" * 70)
    
    # Contar archivos por carpeta
    folders = {
        '📥 Queue': QUEUE_DIR,
        '✅ Approved': APPROVED_DIR,
        '📤 Reviewed': REVIEWED_DIR,
        '💾 Backups': BACKUP_DIR
    }
    
    for label, folder in folders.items():
        if os.path.exists(folder):
            count = len([f for f in os.listdir(folder) if f.endswith('.json')])
            print(f"   {label}: {count} archivos")
    
    # Tamaño del JSON principal
    if os.path.exists(MAIN_JSON):
        size_mb = os.path.getsize(MAIN_JSON) / (1024 * 1024)
        print(f"\n   📄 JSON principal: {size_mb:.2f}MB")
        
        with open(MAIN_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   📋 Entradas totales: {len(data)}")
        pro_count = sum(1 for v in data.values() if v.get('pro'))
        print(f"   🔐 Entradas PRO: {pro_count}")
    
    print("=" * 70)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Motor de enriquecimiento seguro')
    parser.add_argument('command', choices=['status', 'generate', 'process', 'import', 'dry-run'], 
                       help='Comando a ejecutar')
    parser.add_argument('--count', type=int, default=5, help='Número de preguntas a generar')
    parser.add_argument('--topic', type=str, help='Tema específico para generar')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        show_status()
    
    elif args.command == 'generate':
        topics = [args.topic] if args.topic else None
        generate_batch(topics=topics, count=args.count)
    
    elif args.command == 'process':
        process_queue()
    
    elif args.command == 'import':
        import_approved_to_main(dry_run=False)
    
    elif args.command == 'dry-run':
        print("🔍 MODO PRUEBA: No se modificará el JSON principal")
        import_approved_to_main(dry_run=True)
    
    else:
        parser.print_help()
