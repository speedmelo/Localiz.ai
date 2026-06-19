from typing import Any


def build_executive_report(
    candidato_id: int,
    ranking_vagas: list[dict[str, Any]],
    interview_questions: dict[str, list[str]],
) -> str:
    """
    Gera parecer executivo objetivo para apoio à recrutadora.
    """

    if not ranking_vagas:
        return (
            f"Candidato {candidato_id}: não foi possível calcular aderência por falta de dados suficientes. "
            "Recomenda-se revisão manual."
        )

    best_job = ranking_vagas[0]

    vaga = best_job.get("vaga", "não identificada")
    score = best_job.get("score_aderencia", 0)
    classificacao = best_job.get("classificacao", "não identificado")
    strengths = best_job.get("pontos_fortes", [])
    weaknesses = best_job.get("pontos_fracos", [])
    red_flags = best_job.get("red_flags", [])

    report = [
        f"Candidato {candidato_id} apresenta melhor aderência para a vaga {vaga}, com score determinístico de {score}% e classificação {classificacao}.",
    ]

    if strengths:
        report.append(f"Principais pontos fortes: {', '.join(strengths[:5])}.")

    if weaknesses:
        report.append(f"Pontos de atenção: {', '.join(weaknesses[:5])}.")

    if red_flags:
        report.append(f"Red flags identificadas: {', '.join(red_flags[:5])}.")
    else:
        report.append("Não foram identificadas red flags críticas nas evidências analisadas.")

    if interview_questions.get("validacao_requisitos"):
        report.append(
            "Recomenda-se validar em entrevista os requisitos ausentes ou incertos antes de qualquer decisão."
        )

    report.append(
        "Este parecer é apoio à decisão. A decisão final deve permanecer com a recrutadora responsável."
    )

    return " ".join(report)
