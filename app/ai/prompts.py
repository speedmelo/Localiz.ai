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
•Vendas
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


def build_candidate_evidence_prompt(curriculo_texto: str) -> str:
    """
    Constrói o prompt para o Gemini extrair evidências do currículo.

    A IA não calcula score final aqui.
    Ela apenas identifica evidências, lacunas e sinais relevantes.
    """

    return f"""
Você é uma IA especialista em Talent Intelligence para recrutamento operacional da Localiza.

Use os requisitos abaixo como referência oficial:

{LOCALIZA_REQUIREMENTS_PROMPT}

MISSÃO:
Analise o currículo do candidato e extraia evidências objetivas para cada vaga.

REGRAS:
- Não invente informações.
- Se não houver evidência no currículo, marque como "não identificado".
- Não calcule score final.
- Não tome decisão de contratação.
- Analise cada vaga separadamente.
- Diferencie ATENDIMENTO, AUXILIAR OPERAÇÃO e AGENTE DE HIGIENIZAÇÃO.
- Identifique requisitos atendidos, não atendidos e não identificados.
- Liste pontos fortes, pontos fracos e red flags.
- Gere perguntas para validar pontos incertos.

CURRÍCULO:
{curriculo_texto}

RETORNE APENAS JSON VÁLIDO, sem markdown e sem texto fora do JSON:

{{
  "candidate_evidence": {{
    "education": {{
      "ensino_fundamental": "atende | não atende | não identificado",
      "ensino_medio": "atende | não atende | não identificado",
      "evidence": ""
    }},
    "driver_license": {{
      "has_cnh_b": "atende | não atende | não identificado",
      "cnh_time": "não identificado | menos de 1 ano | 1 ano ou mais | 2 anos ou mais",
      "evidence": ""
    }},
    "experience": {{
      "customer_service": "atende | não atende | não identificado",
      "sales": "atende | não atende | não identificado",
      "negotiation": "atende | não atende | não identificado",
      "physical_effort": "atende | não atende | não identificado",
      "office_package": "atende | não atende | não identificado",
      "evidence": ""
    }},
    "availability": {{
      "scale_6x1": "atende | não atende | não identificado",
      "weekends_holidays": "atende | não atende | não identificado",
      "saturdays_6h": "atende | não atende | não identificado",
      "flexible_shifts": "atende | não atende | não identificado",
      "evidence": ""
    }},
    "communication": {{
      "communication_skill": "baixo | medio | alto | não identificado",
      "evidence": ""
    }}
  }},
  "job_analysis": [
    {{
      "job": "ATENDIMENTO",
      "requirements_met": [],
      "requirements_not_met": [],
      "requirements_unknown": [],
      "strengths": [],
      "weaknesses": [],
      "red_flags": [],
      "interview_questions": []
    }},
    {{
      "job": "AUXILIAR OPERAÇÃO",
      "requirements_met": [],
      "requirements_not_met": [],
      "requirements_unknown": [],
      "strengths": [],
      "weaknesses": [],
      "red_flags": [],
      "interview_questions": []
    }},
    {{
      "job": "AGENTE DE HIGIENIZAÇÃO",
      "requirements_met": [],
      "requirements_not_met": [],
      "requirements_unknown": [],
      "strengths": [],
      "weaknesses": [],
      "red_flags": [],
      "interview_questions": []
    }}
  ],
  "general_summary": "",
  "human_review_required": true
}}
"""
