# app/api/v1/endpoints/upload.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import json

from app.services.pdf_service import extrair_texto_pdf
from app.services.candidate_service import analisar_varios_candidatos

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