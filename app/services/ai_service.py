import json
import os
import re
from typing import Any

from google import genai
from google.genai import types  # Importado para forçar o JSON estrito
from app.core.logging import get_logger

logger = get_logger("ia_service")

LOCALIZA_REQUIREMENTS_PROMPT = """
agora para deixar ela 100% do que a localiza quer!!! Ela quer esses requisitos
estrutura i.a
Descrição da vaga / ATENDIMENTO
O QUE PRECISAMOS
Disponibilidade para atuar em escala 6x1;
Ensino Médio completo;
Ótima capacidade de comunicação;
Experiência prévia em atendimento ao cliente;
Conhecimento em pacote office;
Capacidade de negociação com o cliente;
CNH categoria B há, no mínimo, 2 anos.
• Disponibilidade para atuar nos fins de semana e feriados, escala 6x1
• Vendas
Descrição da vaga / AUXILIAR OPERAÇÃO
CNH categoria B há, no mínimo, 1 ano
• Ensino Médio completo
• Experiência prévia em atendimento ao cliente
• Conhecimento em pacote office
• Atendimento ao cliente
 Descrição da vaga/Agente de higienização
Ensino Fundamental completo;
CNH categoria B ativa;
Experiência prévia em atividades que exigem esforço físico;
Disponibilidade para atuar em escalas aos sábados, carga horária de 6h por dia;
Flexibilidade para trabalhar em diferentes turnos (manhã ou tarde), conforme necessidade da operação.
"""

class AIService:
    @staticmethod
    def get_client() -> genai.Client:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY não configurada no .env")
        return genai.Client(api_key=api_key)

    @staticmethod
    def safe_json(texto: str) -> dict[str, Any]:
        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", texto, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        logger.warning("Falha ao parsear JSON da IA.")
        return {
            "erro": "Falha ao interpretar resposta da IA",
            "resposta_bruta": texto,
        }

    @staticmethod
    def build_prompt(curriculo_texto: str) -> str:
        return f"""
Você é uma IA especialista em Talent Intelligence, recrutamento, seleção e análise de aderência para vagas da Localiza.

Sua função é analisar o currículo do candidato e identificar qual vaga possui maior aderência.

Use obrigatoriamente os requisitos abaixo como referência principal:

{LOCALIZA_REQUIREMENTS_PROMPT}

REGRAS DE RACIOCÍNIO DE GEOLOCALIZAÇÃO (ABRANGÊNCIA EXPANDIDA):
- O candidato pode NÃO ter preenchido o CEP. Procure ativamente no currículo por nomes de rua, avenidas, bairros, cidade ou estado.
- Avalie a proximidade e a facilidade de deslocamento do candidato para as filiais operacionais da Localiza com base no endereço textual por extenso encontrado.
- Caso o endereço mapeado por nome de rua indique alta distância ou inviabilidade de transporte para os turnos da vaga, aponte isso como um ponto fraco ou risco de logística na respectiva vaga.

REGRAS DE RACIOCÍNIO GERAIS:
- Cada vaga possui necessidades específicas.
- Não trate todas as vagas como iguais.
- Compare o candidato contra cada vaga separadamente.
- Calcule a aderência de forma individual para ATENDIMENTO, AUXILIAR OPERAÇÃO e AGENTE DE HIGIENIZAÇÃO.
- O score deve refletir o quanto o candidato atende aos requisitos obrigatórios e desejáveis de cada vaga.
- Se uma informação não estiver no currículo, marque como "não identificado".
- Não invente experiências, CNH, escolaridade, disponibilidade ou habilidades.
- Dê maior peso para requisitos obrigatórios como CNH, escolaridade, experiência e disponibilidade.
- Explique por que uma vaga ficou melhor ranqueada que outra.
- Gere perguntas de entrevista para validar pontos incertos.
- A decisão final sempre deve ser da recrutadora.
- Nunca dê outro score diferente para o mesmo candidato analisado, mantenha o mesmo score pela aderencia do curriculo apresentado no pdf.

CURRÍCULO DO CANDIDATO:
{curriculo_texto}

RETORNE APENAS UM JSON VÁLIDO SEGUINDO EXATAMENTE A ESTRUTURA ABAIXO:

{{
  "melhor_vaga": "",
  "ranking_vagas": [
    {{
      "vaga": "ATENDIMENTO",
      "score_aderencia": 0,
      "classificacao": "baixo | medio | alto | excelente",
      "pontos_fortes": [],
      "pontos_fracos": [],
      "requisitos_atendidos": [],
      "requisitos_nao_atendidos": [],
      "requisitos_nao_identificados": [],
      "justificativa": ""
    }},
    {{
      "vaga": "AUXILIAR OPERAÇÃO",
      "score_aderencia": 0,
      "classificacao": "baixo | medio | alto | excelente",
      "pontos_fortes": [],
      "pontos_fracos": [],
      "requisitos_atendidos": [],
      "requisitos_nao_atendidos": [],
      "requisitos_nao_identificados": [],
      "justificativa": ""
    }},
    {{
      "vaga": "AGENTE DE HIGIENIZAÇÃO",
      "score_aderencia": 0,
      "classificacao": "baixo | medio | alto | excelente",
      "pontos_fortes": [],
      "pontos_fracos": [],
      "requisitos_atendidos": [],
      "requisitos_nao_atendidos": [],
      "requisitos_nao_identificados": [],
      "justificativa": ""
    }}
  ],
  "nivel_candidato": "junior | pleno | senior | não identificado",
  "risco_contratacao": "baixo | medio | alto",
  "red_flags": [],
  "perguntas_entrevista": {{
    "tecnicas": [],
    "comportamentais": [],
    "validacao_requisitos": []
  }},
  "parecer_executivo": "",
  "recomendacao_final": ""
}}
"""

    @classmethod
    async def analisar_candidato(cls, curriculo_texto: str) -> dict[str, Any]:
        client = cls.get_client()
        prompt = cls.build_prompt(curriculo_texto)

        try:
            # Configuração Sênior: Força o modelo a responder estritamente em JSON válido
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

            texto_resposta = response.text or ""
            resultado = cls.safe_json(texto_resposta)
            logger.info("Análise de candidato concluída com sucesso.")
            return resultado

        except Exception as exc:
            logger.exception("Erro ao analisar candidato com Gemini.")
            return {
                "erro": "Erro ao analisar candidato",
                "detalhe": str(exc),
            }