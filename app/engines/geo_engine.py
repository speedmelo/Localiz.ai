def calculate_geo_score(
    distancia_km: float | None,
    raio_ideal_km: float = 7.0,
    raio_maximo_km: float = 20.0,
) -> int:
    """
    Calcula score geográfico simples e determinístico.

    100 = dentro do raio ideal.
    0 = acima do raio máximo.
    """

    if distancia_km is None:
        return 0

    if distancia_km <= raio_ideal_km:
        return 100

    if distancia_km >= raio_maximo_km:
        return 0

    score = 100 * (1 - ((distancia_km - raio_ideal_km) / (raio_maximo_km - raio_ideal_km)))

    return max(0, min(100, round(score)))
