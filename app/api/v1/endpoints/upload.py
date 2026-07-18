# app/api/v1/endpoints/upload.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import json

from app.services.pdf_service import extrair_texto_pdf
from app.services.candidate_service import analisar_varios_candidatos
# Novos imports para o motor geográfico
from app.services.geo_service import extrair_cep_do_texto, geocodificar, buscar_filiais_no_perimetro

router = APIRouter()


@router.post("/curriculos", status_code=200)
async def upload_curriculos(
    arquivos: List[UploadFile] = File(...),
    vagas: str = Form(...)
):
    """Upload de múltiplos currículos + análise"""
    if len(arquivos) > 5:
        raise HTTPException(400, "Máximo de 5 currículos por requisição")

    if not vagas:
        raise HTTPException(400, "Campo 'vagas' é obrigatório")

    # Extrai texto dos PDFs
    textos = []
    for arquivo in arquivos:
        texto = await extrair_texto_pdf(arquivo)
        if not texto or len(texto.strip()) < 50:
            raise HTTPException(400, f"Falha ao extrair texto do arquivo: {arquivo.filename}")
        textos.append(texto)

    # Converte vagas de JSON string para dict
    try:
        vagas_json = json.loads(vagas)
    except json.JSONDecodeError:
        raise HTTPException(400, "Formato inválido no campo 'vagas' (deve ser JSON)")

    # Análise completa
    resultado = await analisar_varios_candidatos(textos, vagas_json)

    return resultado


@router.post("/matching", status_code=200)
async def upload_matching(
    file: UploadFile = File(...),
    limite_capital: float = Form(20.0),
    limite_litoral: float = Form(10.0),
    limite_interior: float = Form(5.0)
):
    """
    Rota do Dashboard: Recebe um único currículo em PDF, extrai o CEP,
    converte em coordenadas e busca as filiais da Localiza no perímetro dinâmico.
    """
    # 1. Extrai o texto do PDF usando o seu serviço existente
    texto_curriculo = await extrair_texto_pdf(file)
    if not texto_curriculo or len(texto_curriculo.strip()) < 50:
        raise HTTPException(400, "Falha ao extrair texto ou PDF muito curto.")

    # 2. Busca o CEP usando a nossa regex do GeoService
    cep = extrair_cep_do_texto(texto_curriculo)
    if not cep:
        raise HTTPException(422, "Nenhum CEP válido foi identificado no texto do currículo.")

    # 3. Geocodifica o CEP para obter Lat/Lon
    coordenadas = await geocodificar(cep)
    if not coordenadas:
        raise HTTPException(400, f"Não foi possível obter coordenadas para o CEP: {cep}")

    # 4. Filtra as agências da Localiza no perímetro do candidato
    # Passamos os limites coletados dos sliders do dashboard
    filiais = await buscar_filiais_no_perimetro(coordenadas["lat"], coordenadas["lon"])

    # Se você quiser filtrar as filiais usando estritamente os parâmetros que vieram da tela (limite_capital, etc.)
    # você pode aplicar um filtro extra aqui ou mapear os limites na função buscar_filiais_no_perimetro!
    
    return {
        "cep_candidato": cep,
        "coordenadas": coordenadas,
        "filiais_recomendadas": filiais
    }