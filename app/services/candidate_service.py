# -*- coding: utf-8 -*-
import asyncio
from typing import Any

from app.services.ai_service import AIService
from app.services.response_service import formatar_resultado_comparacao

ai_service = AIService()

MAX_CANDIDATOS_COMPARACAO = 5


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
    curriculos: list[str]
) -> dict[str, Any]:
    """
    Analisa múltiplos currículos em paralelo cruzando com as vagas da Localiza.
    """
    if not curriculos:
        raise ValueError("É necessário informar pelo menos 1 currículo.")

    if len(curriculos) > MAX_CANDIDATOS_COMPARACAO:
        raise ValueError(f"A comparação permite no máximo {MAX_CANDIDATOS_COMPARACAO} candidatos.")

    # Correção Senior: Passa apenas curriculo_texto conforme a assinatura real do AIService
    tarefas = [
        ai_service.analisar_candidato(curriculo_texto=texto)
        for texto in curriculos
    ]
    
    analises_ia = await asyncio.gather(*tarefas)

    resultados: list[dict[str, Any]] = []

    for index, analise in enumerate(analises_ia, start=1):
        resultados.append(
            {
                "candidato_id": index,
                "melhor_vaga": analise.get("melhor_vaga"),
                "score": _extrair_melhor_score(analise),
                "risco_contratacao": analise.get("risco_contratacao"),
                "parecer_executivo": analise.get("parecer_executivo"),
                "endereco_identificado": analise.get("endereco_extraido", "Não identificado"),
                "analise_completa": analise,
            }
        )

    ranking = sorted(
        resultados,
        key=lambda candidato: candidato.get("score", 0),
        reverse=True,
    )

    return formatar_resultado_comparacao(ranking)