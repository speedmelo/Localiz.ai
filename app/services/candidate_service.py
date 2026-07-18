# -*- coding: utf-8 -*-
import asyncio
from typing import Any

# Correção Senior: Importando a classe conforme a arquitetura real do projeto
from app.services.ai_service import AIService
from app.services.response_service import formatar_resultado_comparacao

# Instanciação única do serviço de IA (Singleton Pattern na prática)
ai_service = AIService()

MAX_CANDIDATOS_COMPARACAO = 5  # Alinhado com o limite de 5 do seu upload.py


def _extrair_melhor_score(analise: dict[str, Any]) -> int:
    """
    Extrai o maior score de aderência do ranking de vagas do candidato.
    """
    ranking_vagas = analise.get("ranking_vagas", [])
    if not ranking_vagas:
        return 0

    melhor = max(
        ranking_vagas,
        key=lambda vaga: vaga.get("score_aderencia", 0),
    )
    return int(melhor.get("score_aderencia", 0))


async def analisar_varios_candidatos(
    curriculos: list[str], 
    vagas: list[dict[str, Any]] | dict[str, Any]
) -> dict[str, Any]:
    """
    Analisa múltiplos currículos em paralelo cruzando com as vagas fornecidas.
    Otimizado com asyncio.gather para performance de escala.
    """
    if not curriculos:
        raise ValueError("É necessário informar pelo menos 1 currículo.")

    if len(curriculos) > MAX_CANDIDATOS_COMPARACAO:
        raise ValueError(f"A comparação permite no máximo {MAX_CANDIDATOS_COMPARACAO} candidatos.")

    # Pulo do Gato Senior: Criamos uma lista de corrotinas para processamento PARALELO
    # Passamos o currículo e a vaga para bater certinho com o seu AIService
    tarefas = [
        ai_service.analisar_candidato(curriculo=texto, vagas=vagas)
        for texto in curriculos
    ]
    
    # Executa todas as chamadas de IA simultaneamente
    analises_ia = await asyncio.gather(*tarefas)

    resultados: list[dict[str, Any]] = []

    # Monta o payload estruturado de resultados
    for index, analise in enumerate(analises_ia, start=1):
        resultados.append(
            {
                "candidato_id": index,
                "melhor_vaga": analise.get("melhor_vaga"),
                "score": _extrair_melhor_score(analise),
                "risco_contratacao": analise.get("risco_contratacao"),
                "parecer_executivo": analise.get("parecer_executivo"),
                "analise_completa": analise,
            }
        )

    # Ordena os candidatos do maior score para o menor
    ranking = sorted(
        resultados,
        key=lambda candidato: candidato.get("score", 0),
        reverse=True,
    )

    return formatar_resultado_comparacao(ranking)