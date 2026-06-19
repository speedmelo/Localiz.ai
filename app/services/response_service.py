from typing import Any


def formatar_resultado_comparacao(
    ranking_candidatos: list[dict[str, Any]],
) -> dict[str, Any]:
    if not ranking_candidatos:
        return {
            "total_candidatos": 0,
            "melhor_candidato": None,
            "ranking": [],
            "parecer_geral": "Nenhum candidato foi informado para análise.",
        }

    ranking_ordenado = sorted(
        ranking_candidatos,
        key=lambda candidato: candidato.get("score", 0),
        reverse=True,
    )

    melhor = ranking_ordenado[0]

    return {
        "total_candidatos": len(ranking_ordenado),
        "melhor_candidato": {
            "candidato_id": melhor.get("candidato_id"),
            "melhor_vaga": melhor.get("melhor_vaga"),
            "score": melhor.get("score"),
            "risco_contratacao": melhor.get("risco_contratacao"),
            "parecer_executivo": melhor.get("parecer_executivo"),
        },
        "ranking": [
            {
                "posicao": index,
                "candidato_id": candidato.get("candidato_id"),
                "melhor_vaga": candidato.get("melhor_vaga"),
                "score": candidato.get("score"),
                "risco_contratacao": candidato.get("risco_contratacao"),
                "parecer_executivo": candidato.get("parecer_executivo"),
            }
            for index, candidato in enumerate(ranking_ordenado, start=1)
        ],
        "analises_completas": [
            candidato.get("analise_completa", {})
            for candidato in ranking_ordenado
        ],
        "parecer_geral": (
            "Ranking gerado com base na aderência dos candidatos às vagas, "
            "considerando requisitos obrigatórios, pontos fortes, lacunas, "
            "riscos e evidências identificadas no currículo."
        ),
    }