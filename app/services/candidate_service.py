from typing import Any

from app.services.ia_service import analisar_candidato
from app.services.response_service import formatar_resultado_comparacao


MAX_CANDIDATOS_COMPARACAO = 3


def _extrair_melhor_score(analise: dict[str, Any]) -> int:
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
) -> dict[str, Any]:
    if not curriculos:
        raise ValueError("É necessário informar pelo menos 1 currículo.")

    if len(curriculos) > MAX_CANDIDATOS_COMPARACAO:
        raise ValueError("A comparação permite no máximo 3 candidatos.")

    resultados: list[dict[str, Any]] = []

    for index, curriculo_texto in enumerate(curriculos, start=1):
        analise = await analisar_candidato(curriculo_texto)

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

    ranking = sorted(
        resultados,
        key=lambda candidato: candidato.get("score", 0),
        reverse=True,
    )

    return formatar_resultado_comparacao(ranking)
