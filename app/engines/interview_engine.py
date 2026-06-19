from typing import Any


DEFAULT_INTERVIEW_QUESTIONS = {
    "ATENDIMENTO": [
        "Conte sobre uma situação em que precisou lidar com um cliente insatisfeito.",
        "Como você organiza sua rotina em uma escala 6x1?",
        "Descreva uma experiência em que precisou negociar com um cliente.",
    ],
    "AUXILIAR OPERAÇÃO": [
        "Conte sobre sua experiência com atendimento ao cliente.",
        "Como você utiliza pacote Office no dia a dia?",
        "Você possui CNH B há quanto tempo e dirige com frequência?",
    ],
    "AGENTE DE HIGIENIZAÇÃO": [
        "Conte sobre experiências anteriores com atividades que exigiam esforço físico.",
        "Você possui disponibilidade para atuar aos sábados por 6 horas?",
        "Como você lida com mudanças de turno entre manhã e tarde?",
    ],
}


def generate_interview_questions(
    ranking_vagas: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """
    Gera perguntas de entrevista com base na melhor vaga e lacunas do candidato.
    """

    if not ranking_vagas:
        return {
            "tecnicas": [],
            "comportamentais": [],
            "validacao_requisitos": [],
        }

    best_job = ranking_vagas[0]
    job_name = best_job.get("vaga", "")
    unknown_requirements = best_job.get("requisitos_nao_identificados", [])
    not_met_requirements = best_job.get("requisitos_nao_atendidos", [])

    validation_questions = []

    for requirement in unknown_requirements[:5]:
        validation_questions.append(
            f"Não encontramos evidência sobre '{requirement}'. Você pode explicar sua experiência ou disponibilidade nesse ponto?"
        )

    for requirement in not_met_requirements[:5]:
        validation_questions.append(
            f"O requisito '{requirement}' parece não atendido no currículo. Existe alguma informação atualizada sobre isso?"
        )

    return {
        "tecnicas": DEFAULT_INTERVIEW_QUESTIONS.get(job_name, [])[:2],
        "comportamentais": [
            "Conte sobre um desafio profissional recente e como você resolveu.",
            "Como você reage quando recebe uma orientação diferente do que esperava?",
        ],
        "validacao_requisitos": validation_questions,
    }
