#!/usr/bin/env python3
"""
PREGUNTAS PENDIENTES - Fontanero Virtual PRO
Captura preguntas que el chatbot no entiende para revisar con IA después
"""

import json
import os
from datetime import datetime

PENDING_FILE = './data/pending/pending_questions.json'

def load_pending():
    """Carga preguntas pendientes existentes"""
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'questions': [], 'stats': {'total': 0, 'answered': 0, 'pending': 0}}

def save_pending(data):
    """Guarda preguntas pendientes"""
    os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)
    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_pending_question(question, user_language='es', context=None):
    """Añade una pregunta que el chatbot no pudo responder"""
    data = load_pending()
    
    # Verificar si ya existe esta pregunta
    normalized = question.lower().strip()
    for q in data['questions']:
        if q['question'].lower().strip() == normalized:
            print(f"⚠️  Pregunta ya registrada: '{question}'")
            q['count'] = q.get('count', 1) + 1
            q['last_asked'] = datetime.now().isoformat()
            save_pending(data)
            return False
    
    # Añadir nueva pregunta
    new_question = {
        'question': question,
        'language': user_language,
        'context': context,
        'timestamp': datetime.now().isoformat(),
        'count': 1,
        'status': 'pending',  # pending, reviewed, answered, rejected
        'suggested_key': None,
        'suggested_answer': None,
        'reviewed_by': None,
        'reviewed_at': None
    }
    
    data['questions'].append(new_question)
    data['stats']['total'] += 1
    data['stats']['pending'] += 1
    
    save_pending(data)
    print(f"✅ Pregunta pendiente añadida: '{question}'")
    return True

def export_for_review(output_file='./data/pending/for_ia_review.json'):
    """Exporta preguntas pendientes para revisar con IA"""
    data = load_pending()
    
    pending = [q for q in data['questions'] if q['status'] == 'pending']
    
    if not pending:
        print("✅ No hay preguntas pendientes para revisar")
        return None
    
    export_data = {
        'exported_at': datetime.now().isoformat(),
        'total_pending': len(pending),
        'questions': []
    }
    
    for q in pending:
        export_data['questions'].append({
            'original_question': q['question'],
            'language': q['language'],
            'count': q['count'],
            'suggested_key': q.get('suggested_key'),
            'needs_answer': True
        })
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exportadas {len(pending)} preguntas para revisar con IA")
    print(f"   Archivo: {output_file}")
    return output_file

def import_reviewed_answers(input_file='./data/pending/ia_reviewed.json'):
    """Importa respuestas revisadas desde IA (con validación)"""
    if not os.path.exists(input_file):
        print(f"❌ Archivo no existe: {input_file}")
        return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reviewed = json.load(f)
    
    # Cargar datos pendientes y principales
    pending_data = load_pending()
    main_json_path = './json/responses.json'
    
    with open(main_json_path, 'r', encoding='utf-8') as f:
        main_data = json.load(f)
    
    added = 0
    skipped = 0
    errors = 0
    
    for item in reviewed.get('reviewed_questions', []):
        question = item.get('original_question')
        suggested_key = item.get('suggested_key')
        answer = item.get('answer')
        
        if not question or not answer:
            errors += 1
            continue
        
        # Normalizar clave
        if not suggested_key:
            suggested_key = question.lower().strip().replace(' ', '_').replace('-', '_')
        
        # Verificar duplicados
        normalized = suggested_key.lower().strip().replace(' ', '_')
        existing_keys = {k.lower().strip().replace(' ', '_'): k for k in main_data.keys()}
        
        if normalized in existing_keys:
            print(f"⚠️  Saltando duplicado: '{suggested_key}' ya existe")
            skipped += 1
            continue
        
        # Crear entrada
        new_entry = {
            'alias': [question],
            'pasos': answer if isinstance(answer, list) else [answer],
            'pro': item.get('pro', False),
            'source': 'ia_reviewed',
            'reviewed_at': datetime.now().isoformat()
        }
        
        # Añadir al JSON principal
        main_data[suggested_key] = new_entry
        added += 1
        
        # Actualizar estado en pending
        for q in pending_data['questions']:
            if q['question'] == question:
                q['status'] = 'answered'
                q['suggested_key'] = suggested_key
                q['reviewed_by'] = 'ia'
                q['reviewed_at'] = datetime.now().isoformat()
                pending_data['stats']['answered'] += 1
                pending_data['stats']['pending'] -= 1
    
    # Guardar cambios
    with open(main_json_path, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, indent=2, ensure_ascii=False)
    
    save_pending(pending_data)
    
    print(f"\n✅ IMPORTACIÓN COMPLETADA:")
    print(f"   • Añadidas: {added}")
    print(f"   • Saltadas (duplicadas): {skipped}")
    print(f"   • Errores: {errors}")
    
    return added > 0

def show_stats():
    """Muestra estadísticas de preguntas pendientes"""
    data = load_pending()
    
    print("\n" + "=" * 70)
    print("📊 ESTADÍSTICAS DE PREGUNTAS PENDIENTES")
    print("=" * 70)
    print(f"   Total registradas: {data['stats']['total']}")
    print(f"   Respondidas: {data['stats']['answered']}")
    print(f"   Pendientes: {data['stats']['pending']}")
    
    # Mostrar últimas 10 pendientes
    pending = [q for q in data['questions'] if q['status'] == 'pending'][-10:]
    if pending:
        print(f"\n📋 ÚLTIMAS PREGUNTAS PENDIENTES:")
        for q in pending:
            print(f"   • '{q['question']}' ({q['count']} veces) [{q['language']}]")
    
    print("=" * 70)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        show_stats()
    else:
        command = sys.argv[1]
        
        if command == 'export':
            export_for_review()
        elif command == 'import':
            file = sys.argv[2] if len(sys.argv) > 2 else './data/pending/ia_reviewed.json'
            import_reviewed_answers(file)
        elif command == 'stats':
            show_stats()
        else:
            print("Comandos disponibles: export, import, stats")
