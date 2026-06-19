import math
from typing import Any

import httpx

from app.core.logging import get_logger

logger = get_logger("geo_service")


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
EARTH_RADIUS_KM = 6371.0
DEFAULT_TIMEOUT_SECONDS = 10.0


async def geocodificar(endereco: str) -> dict[str, float] | None:
    """
    Converte um endereço em latitude/longitude usando Nominatim OpenStreetMap.
    """

    if not endereco or not endereco.strip():
        return None

    params = {
        "q": endereco.strip(),
        "format": "json",
        "limit": 1,
    }

    headers = {
        "User-Agent": "LocalizAI-MeloStrategicAI/1.0",
    }

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
            response = await client.get(
                NOMINATIM_URL,
                params=params,
                headers=headers,
            )

        response.raise_for_status()
        data = response.json()

        if not data:
            return None

        location = data[0]

        return {
            "lat": float(location["lat"]),
            "lon": float(location["lon"]),
        }

    except Exception as exc:
        logger.warning("Erro ao geocodificar endereço: %s", exc)
        return None


def calcular_distancia_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calcula distância aproximada entre duas coordenadas usando Haversine.
    """

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return EARTH_RADIUS_KM * c


async def buscar_vagas_proximas(
    endereco_candidato: str,
    vagas: list[dict[str, Any]],
    raio_km: float = 7.0,
) -> list[dict[str, Any]]:
    """
    Retorna vagas dentro de um raio de distância do endereço do candidato.
    """

    origem = await geocodificar(endereco_candidato)

    if not origem:
        return []

    resultados: list[dict[str, Any]] = []

    for vaga in vagas:
        endereco_vaga = vaga.get("endereco")

        if not endereco_vaga:
            continue

        destino = await geocodificar(endereco_vaga)

        if not destino:
            continue

        distancia = calcular_distancia_km(
            origem["lat"],
            origem["lon"],
            destino["lat"],
            destino["lon"],
        )

        if distancia <= raio_km:
            resultados.append(
                {
                    "nome": vaga.get("nome", ""),
                    "endereco": endereco_vaga,
                    "descricao": vaga.get("descricao", ""),
                    "distancia_km": round(distancia, 2),
                }
            )

    return sorted(
        resultados,
        key=lambda item: item["distancia_km"],
    )
