from typing import Any


def rank_candidates(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Ordena candidatos pelo maior score calculado.
    """

    return sorted(
        candidates,
        key=lambda candidate: candidate.get("score", 0),
        reverse=True,
    )


def build_candidate_ranking_item(
    candidato_id: int,
    ai_result: dict[str, Any],
    job_scores: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Monta um item de ranking padronizado para um candidato.
    """

    best_job = job_scores[0] if job_scores else {}

    return {
        "candidato_id": candidato_id,
        "melhor_vaga": best_job.get("vaga"),
        "score": best_job.get("score_aderencia", 0),
        "classificacao": best_job.get("classificacao"),
        "risco_contratacao": infer_hiring_risk(best_job),
        "ranking_vagas": job_scores,
        "evidencias": ai_result.get("candidate_evidence", {}),
        "resumo_ia": ai_result.get("general_summary", ""),
        "human_review_required": True,
    }


def infer_hiring_risk(best_job: dict[str, Any]) -> str:
    score = int(best_job.get("score_aderencia", 0))
    red_flags = best_job.get("red_flags", [])

    if red_flags or score < 50:
        return "alto"

    if score < 75:
        return "medio"

    return "baixo"
