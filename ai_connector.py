#!/usr/bin/env python3
"""
CONECTOR CON IA - Fontanero Virtual PRO
Genera respuestas técnicas usando ChatGPT API de forma controlada
"""

import json
import os
import sys
from datetime import datetime

# Configuración (pon tu API key en variable de entorno)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
APPROVED_DIR = './approved'
REVIEWED_DIR = './reviewed'
MAIN_JSON = './json/responses.json'

def load_approved_questions():
    """Carga preguntas aprobadas listas para IA"""
    questions = []
    
    for filename in os.listdir(APPROVED_DIR):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(APPROVED_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        key = list(data.keys())[0]
        entry = data[key]
        
        questions.append({
            'filename': filename,
            'key': key,
            'question': entry.get('alias', [key])[0],
            'category': entry.get('category', 'general'),
            'pro': entry.get('pro', False),
            'source': entry.get('source', 'auto_generated')
        })
    
    return questions

def generate_ai_response(question_data):
    """Genera respuesta usando ChatGPT API (simulado si no hay key)"""
    
    if not OPENAI_API_KEY:
        # Modo simulación para pruebas
        return {
            'pasos': [
                f'[SIMULACIÓN] Respuesta para: {question_data["question"]}',
                '💰 Presupuesto orientativo: 50-150€ estimado',
                'Para valoración exacta, envíame foto por WhatsApp 📸'
            ],
            'alias': [question_data['question']],
            'pro': question_data.get('pro', False),
            'source': 'ia_simulated',
            'generated_at': datetime.now().isoformat()
        }
    
    # Modo real con OpenAI API
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""Eres un experto fontanero profesional en España.
Responde a esta pregunta técnica de forma clara y útil:

Pregunta: "{question_data['question']}"
Categoría: {question_data['category']}
¿Es contenido PRO/técnico? {'Sí' if question_data.get('pro') else 'No'}

Formato de respuesta requerido:
1. Lista de pasos claros y prácticos (máximo 5)
2. Si aplica, incluye presupuesto orientativo con formato: "💰 Presupuesto orientativo: XX-YY€"
3. Siempre termina con: "Para valoración exacta, envíame foto por WhatsApp 📸"
4. Si es producto, menciona catálogo Webador: "🔗 Consulta en: https://fontaneriaeduardoquiroz.webador.es"

Responde SOLO con el array de pasos, sin explicaciones adicionales."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        steps_text = response.choices[0].message.content.strip()
        
        # Parsear respuesta a lista
        steps = [s.strip() for s in steps_text.split('\n') if s.strip() and not s.strip().startswith('```')]
        
        return {
            'pasos': steps,
            'alias': [question_data['question']],
            'pro': question_data.get('pro', False),
            'source': 'ia_generated',
            'generated_at': datetime.now().isoformat(),
            'model': 'gpt-4o-mini'
        }
        
    except ImportError:
        print("⚠️  OpenAI library no instalada: pip install openai")
        return None
    except Exception as e:
        print(f"❌ Error con IA: {e}")
        return None

def process_with_ai():
    """Procesa preguntas aprobadas generando respuestas con IA"""
    questions = load_approved_questions()
    
    if not questions:
        print("✅ No hay preguntas aprobadas para procesar con IA")
        return 0
    
    print(f"🤖 Procesando {len(questions)} preguntas con IA...")
    
    processed = 0
    failed = 0
    
    for q in questions:
        print(f"\n🔹 Generando respuesta para: {q['question'][:60]}...")
        
        response = generate_ai_response(q)
        
        if response:
            # Crear archivo con respuesta completa
            entry = {
                q['key']: {
                    **response,
                    'original_question': q['question'],
                    'reviewed': False,
                    'ready_for_import': True
                }
            }
            
            # Guardar en reviewed/
            output_path = os.path.join(REVIEWED_DIR, q['filename'])
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(entry, f, indent=2, ensure_ascii=False)
            
            # Eliminar de approved/
            os.remove(os.path.join(APPROVED_DIR, q['filename']))
            
            print(f"✅ Respuesta generada: {output_path}")
            processed += 1
        else:
            print(f"❌ Falló generar respuesta para: {q['key']}")
            failed += 1
    
    print(f"\n📊 IA completada: {processed} generadas, {failed} fallidas")
    return processed

def review_and_approve(filepath):
    """Marca una respuesta como revisada y lista para importar"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    key = list(data.keys())[0]
    data[key]['reviewed'] = True
    data[key]['reviewed_at'] = datetime.now().isoformat()
    data[key]['reviewed_by'] = 'human'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {key} marcado como revisado y listo para importar")
    return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Conector con IA para enriquecimiento')
    parser.add_argument('command', choices=['process', 'review'], help='Comando')
    parser.add_argument('--file', type=str, help='Archivo específico para review')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        process_with_ai()
    
    elif args.command == 'review':
        if args.file:
            review_and_approve(args.file)
        else:
            print("❌ Especifica --file con la ruta del archivo a revisar")
    
    else:
        parser.print_help()
