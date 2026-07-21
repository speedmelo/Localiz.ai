# -*- coding: utf-8 -*-
import io
import json
import os
import re
from typing import Any, List, Optional

from google import genai
from google.genai import types
from pypdf import PdfReader
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
    def extrair_texto_de_pdf(pdf_bytes: bytes) -> str:
        """Extrai o texto puro de um PDF enviado em bytes de forma segura."""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            texto_extraido = ""
            for page in reader.pages:
                texto_extraido += (page.extract_text() or "") + "\n"
            return texto_extraido.strip()
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            raise ValueError("Não foi possível ler o arquivo PDF enviado. Certifique-se de que é um PDF válido.")

    @staticmethod
    def build_prompt(curriculo_texto: str, vagas_customizadas: Optional[List[Any]] = None) -> str:
        req_context = LOCALIZA_REQUIREMENTS_PROMPT
        if vagas_customizadas:
            req_context += f"\n\nVAGAS ADICIONAIS FORNECIDAS NA REQUISIÇÃO:\n{json.dumps(vagas_customizadas, ensure_ascii=False)}"

        return f"""
Você é uma IA especialista em Talent Intelligence, recrutamento, seleção e análise de aderência para vagas da Localiza.

Sua função é analisar o currículo do candidato e identificar qual vaga possui maior aderência.

Use obrigatoriamente os requisitos abaixo como referência principal:

{req_context}

REGRAS DE EXTRAÇÃO E RACIOCÍNIO DE GEOLOCALIZAÇÃO:
- O candidato pode NÃO ter preenchido o CEP. Procure ativamente no currículo pelo endereço completo contendo nome de rua, avenida, servidão, número, bairro, cidade e estado.
- Extraia a linha inteira do endereço encontrado para a chave "endereco_extraido". Exemplo: "Rua da Servidão, 140 - Três Pontes, Amparo/SP".
- Avalie a proximidade e a facilidade de deslocamento do candidato para as filiais operacionais da Localiza com base no endereço textual por extenso.
- Caso o endereço mapeado por nome de rua indique alta distância ou inviabilidade de transporte para os turnos da vaga, aponte isso como ponto fraco ou risco de logística na respectiva vaga.

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
  "endereco_extraido": "linha exata do endereço encontrada no currículo (ex: Rua, Bairro, Cidade/UF)",
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

    async def analisar_candidato(self, curriculo: str, vagas: Optional[List[Any]] = None) -> dict[str, Any]:
        """Método principal para requisições via JSON/Payload (usado no main.py e match.py)."""
        if not curriculo or not curriculo.strip():
            raise ValueError("O conteúdo do currículo não pode estar vazio.")

        client = self.get_client()
        prompt = self.build_prompt(curriculo_texto=curriculo, vagas_customizadas=vagas)

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

            texto_resposta = response.text or ""
            resultado = self.safe_json(texto_resposta)
            logger.info("Análise de candidato por texto/JSON concluída com sucesso.")
            return resultado

        except Exception as exc:
            logger.exception("Erro ao analisar candidato com Gemini.")
            raise RuntimeError(f"Erro na comunicação com a IA Gemini: {str(exc)}")

    async def analisar_candidato_por_pdf(self, pdf_bytes: bytes, filename: str) -> dict[str, Any]:
        """Método auxiliar para requisições com upload de arquivo PDF."""
        texto_curriculo = self.extrair_texto_de_pdf(pdf_bytes)
        
        if not texto_curriculo:
            raise ValueError("O PDF enviado está vazio ou não foi possível extrair texto dele.")

        return await self.analisar_candidato(curriculo=texto_curriculo)