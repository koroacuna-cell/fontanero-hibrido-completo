import json
import re
from unidecode import unidecode
from difflib import SequenceMatcher

class MotorIA:

    def __init__(self, diccionario_path="diccionario_motor_ia.json"):
        with open(diccionario_path, "r", encoding="utf-8") as f:
            self.dicc = json.load(f)

    def normalizar(self, texto):
        texto = unidecode(texto.lower())
        texto = re.sub(r"[^a-z0-9ñáéíóúü ]", " ", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    def similitud(self, a, b):
        """
        Función de similitud mejorada:
        - Normaliza antes de comparar
        - Bono por coincidencia exacta
        - Penaliza diferencias grandes de longitud
        """
        a_norm = self.normalizar(a)
        b_norm = self.normalizar(b)
        score_base = SequenceMatcher(None, a_norm, b_norm).ratio()

        if a_norm == b_norm:
            score_base = max(score_base, 0.95)

        len_diff = abs(len(a_norm) - len(b_norm))
        penalty = len_diff / max(len(a_norm), len(b_norm)) if max(len(a_norm), len(b_norm)) > 0 else 0
        score = score_base * (1 - penalty * 0.2)

        return round(score, 3)

    def evaluar(self, texto_cliente):
        texto_norm = self.normalizar(texto_cliente)
        resultados = []

        for etiqueta, frases in self.dicc.items():
            coincidencias = []
            for frase in frases:
                frase_norm = self.normalizar(frase)
                score = self.similitud(texto_norm, frase_norm)
                if score >= 0.40:
                    coincidencias.append([frase, score])
            if coincidencias:
                mejor_score = max(c[1] for c in coincidencias)
                resultados.append({
                    "etiqueta": etiqueta,
                    "porcentaje": round(mejor_score * 100, 1),
                    "coincidencias": coincidencias
                })

        # Ordenar por porcentaje descendente
        resultados.sort(key=lambda x: x["porcentaje"], reverse=True)
        return resultados
