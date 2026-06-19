from typing import Any


STATUS_POINTS = {
    "atende": 1.0,
    "não atende": 0.0,
    "nao atende": 0.0,
    "não identificado": 0.0,
    "nao identificado": 0.0,
}


JOB_WEIGHTS = {
    "ATENDIMENTO": {
        "ensino_medio": 10,
        "communication_skill": 15,
        "customer_service": 20,
        "office_package": 10,
        "negotiation": 15,
        "has_cnh_b": 15,
        "cnh_2_years": 10,
        "scale_6x1": 5,
    },
    "AUXILIAR OPERAÇÃO": {
        "has_cnh_b": 20,
        "cnh_1_year": 15,
        "ensino_medio": 15,
        "customer_service": 25,
        "office_package": 15,
        "communication_skill": 10,
    },
    "AGENTE DE HIGIENIZAÇÃO": {
        "ensino_fundamental": 15,
        "has_cnh_b": 20,
        "physical_effort": 25,
        "saturdays_6h": 15,
        "flexible_shifts": 15,
        "communication_skill": 10,
    },
}


def _normalize_status(value: Any) -> str:
    if not isinstance(value, str):
        return "não identificado"

    return value.strip().lower()


def _status_score(value: Any) -> float:
    status = _normalize_status(value)
    return STATUS_POINTS.get(status, 0.0)


def _communication_score(value: Any) -> float:
    status = _normalize_status(value)

    if status == "alto":
        return 1.0

    if status == "medio" or status == "médio":
        return 0.7

    if status == "baixo":
        return 0.3

    return 0.0


def _cnh_time_score(value: Any, required_years: int) -> float:
    status = _normalize_status(value)

    if required_years == 2:
        return 1.0 if "2 anos" in status else 0.0

    if required_years == 1:
        return 1.0 if "1 ano" in status or "2 anos" in status else 0.0

    return 0.0


def _get_candidate_evidence(ai_result: dict[str, Any]) -> dict[str, Any]:
    return ai_result.get("candidate_evidence", {}) or {}


def _extract_features(ai_result: dict[str, Any]) -> dict[str, float]:
    evidence = _get_candidate_evidence(ai_result)

    education = evidence.get("education", {}) or {}
    driver_license = evidence.get("driver_license", {}) or {}
    experience = evidence.get("experience", {}) or {}
    availability = evidence.get("availability", {}) or {}
    communication = evidence.get("communication", {}) or {}

    return {
        "ensino_fundamental": _status_score(education.get("ensino_fundamental")),
        "ensino_medio": _status_score(education.get("ensino_medio")),
        "has_cnh_b": _status_score(driver_license.get("has_cnh_b")),
        "cnh_1_year": _cnh_time_score(driver_license.get("cnh_time"), required_years=1),
        "cnh_2_years": _cnh_time_score(driver_license.get("cnh_time"), required_years=2),
        "customer_service": _status_score(experience.get("customer_service")),
        "sales": _status_score(experience.get("sales")),
        "negotiation": _status_score(experience.get("negotiation")),
        "physical_effort": _status_score(experience.get("physical_effort")),
        "office_package": _status_score(experience.get("office_package")),
        "scale_6x1": _status_score(availability.get("scale_6x1")),
        "weekends_holidays": _status_score(availability.get("weekends_holidays")),
        "saturdays_6h": _status_score(availability.get("saturdays_6h")),
        "flexible_shifts": _status_score(availability.get("flexible_shifts")),
        "communication_skill": _communication_score(communication.get("communication_skill")),
    }


def _classify_score(score: int) -> str:
    if score >= 90:
        return "excelente"

    if score >= 75:
        return "alto"

    if score >= 50:
        return "medio"

    return "baixo"


def calculate_job_scores(ai_result: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Calcula score determinístico por vaga.

    A IA extrai evidências.
    Esta engine calcula a aderência.
    """

    features = _extract_features(ai_result)
    job_analysis = {
        item.get("job"): item
        for item in ai_result.get("job_analysis", [])
        if isinstance(item, dict)
    }

    scores: list[dict[str, Any]] = []

    for job_name, weights in JOB_WEIGHTS.items():
        total_weight = sum(weights.values())
        achieved = sum(
            features.get(feature, 0.0) * weight
            for feature, weight in weights.items()
        )

        final_score = round((achieved / total_weight) * 100) if total_weight else 0
        analysis = job_analysis.get(job_name, {}) or {}

        scores.append(
            {
                "vaga": job_name,
                "score_aderencia": int(final_score),
                "classificacao": _classify_score(int(final_score)),
                "pontos_fortes": analysis.get("strengths", []),
                "pontos_fracos": analysis.get("weaknesses", []),
                "red_flags": analysis.get("red_flags", []),
                "requisitos_atendidos": analysis.get("requirements_met", []),
                "requisitos_nao_atendidos": analysis.get("requirements_not_met", []),
                "requisitos_nao_identificados": analysis.get("requirements_unknown", []),
                "justificativa": _build_score_explanation(job_name, weights, features),
            }
        )

    return sorted(
        scores,
        key=lambda item: item["score_aderencia"],
        reverse=True,
    )


def _build_score_explanation(
    job_name: str,
    weights: dict[str, int],
    features: dict[str, float],
) -> str:
    met = [
        feature
        for feature in weights
        if features.get(feature, 0.0) > 0
    ]

    missing = [
        feature
        for feature in weights
        if features.get(feature, 0.0) == 0
    ]

    return (
        f"Score calculado para {job_name} com base em pesos determinísticos. "
        f"Critérios com evidência: {', '.join(met) if met else 'nenhum'}. "
        f"Critérios ausentes ou não identificados: {', '.join(missing) if missing else 'nenhum'}."
    )
