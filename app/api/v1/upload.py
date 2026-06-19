from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.pdf_service import extrair_texto_pdf
from app.services.candidate_service import analisar_varios_candidatos

router = APIRouter()

@router.post("/upload-curriculos")
async def upload_curriculos(
    arquivos: List[UploadFile] = File(...),
    vagas: str = Form(...)
):
    if len(arquivos) > 3:
        return {"erro": "Máximo de 3 currículos por análise"}

    textos = []

    for arquivo in arquivos:
        texto = extrair_texto_pdf(arquivo)
        textos.append(texto)

    import json
    vagas_json = json.loads(vagas)

    resultado = await analisar_varios_candidatos(textos, vagas_json)

    return resultado