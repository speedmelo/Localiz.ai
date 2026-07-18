# -*- coding: utf-8 -*-
import asyncio
import math
import re
from typing import Any
import httpx
from app.core.logging import get_logger

logger = get_logger("geo_service")

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
EARTH_RADIUS_KM = 6371.0
DEFAULT_TIMEOUT_SECONDS = 10.0

# Regex Senior para captura de CEP (com ou sem hífen)
CEP_REGEX = re.compile(r"\b\d{5}-\d{3}\b|\b\d{8}\b")


def extrair_cep_do_texto(texto: str) -> str | None:
    """
    Busca de forma eficiente a primeira ocorrência de um padrão de CEP no texto do currículo.
    """
    if not texto:
        return None
    match = CEP_REGEX.search(texto)
    return match.group(0) if match else None


async def geocodificar(endereco: str) -> dict[str, float] | None:
    """
    Converte um endereço ou CEP em latitude/longitude usando Nominatim OpenStreetMap.
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
            response = await client.get(NOMINATIM_URL, params=params, headers=headers)
        
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
        logger.warning(f"Falha ao geocodificar o endereço '{endereco}': {exc}")
        return None


def calcular_distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula distância aproximada entre duas coordenadas usando a fórmula de Haversine.
    """
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


async def buscar_filiais_no_perimetro(
    endereco_candidato: str,
    vagas: list[dict[str, Any]],
    raio_km: float = 7.0,
) -> list[dict[str, Any]]:
    """
    Retorna as vagas (filiais) dentro do perímetro estipulado.
    Otimizado com asyncio.gather para geocodificação simultânea.
    """
    origem = await geocodificar(endereco_candidato)
    if not origen:
        logger.warning(f"Não foi possível determinar a localização de origem para: {endereco_candidato}")
        return []

    # Passo 1: Filtrar vagas com endereço e preparar chamadas paralelas
    vagas_validas = [vaga for vaga in vagas if vaga.get("endereco")]
    
    if not vagas_validas:
        return []

    # Passo 2: Disparar todas as geocodificações HTTP ao MESMO TEMPO
    tarefas = [geocodificar(vaga["endereco"]) for vaga in vagas_validas]
    destinos = await asyncio.gather(*tarefas)

    resultados: list[dict[str, Any]] = []

    # Passo 3: Processar distâncias com os dados resolvidos
    for vaga, destino in zip(vagas_validas, destinos):
        if not destino:
            continue

        distancia = calcular_distancia_km(
            origem["lat"], origem["lon"],
            destino["lat"], destino["lon"]
        )

        if distancia <= raio_km:
            resultados.append(
                {
                    "nome": vaga.get("nome", ""),
                    "endereco": vaga.get("endereco"),
                    "descricao": vaga.get("descricao", ""),
                    "distancia_km": round(distancia, 2),
                }
            )

    return sorted(resultados, key=lambda item: item["distancia_km"])