# -*- coding: utf-8 -*-
import time
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Request

from app.core.logging import get_logger
from app.services.pdf_service import extrair_texto_upload_pdf, extrair_linha_endereco
from app.services.candidate_service import analisar_varios_candidatos

logger = get_logger("upload_api")
router = APIRouter()

MAX_FILES = 3
ALLOWED_MIME_TYPES = {"application/pdf"}

def _validar_cabecalho_pdf(upload_file: UploadFile) -> bool:
    if upload_file.content_type not in ALLOWED_MIME_TYPES:
        return False
    return True

# A rota fica limpa aqui porque o router.py já coloca o /upload no prefixo!
@router.post(
    "/candidates-matching",
    status_code=status.HTTP_200_OK,
    summary="Upload e Matching Inteligente de Currículos",
    description="Processa até 3 PDFs em paralelo, extrai localização e executa o Matching de IA Localiza."
)
async def upload_matching(
    request: Request,
    files: List[UploadFile] = File(..., description="Lista de arquivos PDF (Máximo 3)")
) -> Dict[str, Any]:
    """
    Endpoint Enterprise de Atração e Seleção de Talentos.
    A URL final no servidor será: /api/v1/upload/candidates-matching
    """
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    logger.info(
        f"[{request_id}] Recebida requisição de upload", 
        extra={"total_arquivos": len(files)}
    )

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo foi enviado."
        )

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limite excedido. Envie no máximo {MAX_FILES} currículos por lote."
        )

    textos_processados: List[str] = []
    enderecos_mapeados: List[str] = []
    metadata_arquivos: List[Dict[str, Any]] = []

    for index, file in enumerate(files, start=1):
        filename = getattr(file, "filename", f"arquivo_{index}.pdf")

        if not _validar_cabecalho_pdf(file):
            logger.warning(f"[{request_id}] Arquivo rejeitado por formato inválido: {filename}")
            metadata_arquivos.append({
                "filename": filename,
                "status": "rejected",
                "motivo": "Formato inválido. Apenas arquivos PDF são aceitos."
            })
            continue

        try:
            texto_extraido = await extrair_texto_upload_pdf(file)
            
            if not texto_extraido or not texto_extraido.strip():
                logger.warning(f"[{request_id}] PDF sem conteúdo legível: {filename}")
                metadata_arquivos.append({
                    "filename": filename,
                    "status": "warning",
                    "motivo": "Arquivo legível, porém nenhum texto selecionável foi extraído."
                })
                continue

            endereco = extrair_linha_endereco(texto_extraido)
            
            textos_processados.append(texto_extraido)
            enderecos_mapeados.append(endereco)

            metadata_arquivos.append({
                "filename": filename,
                "status": "success",
                "bytes_lidos": len(texto_extraido),
                "endereco_identificado": endereco
            })

        except Exception as exc:
            logger.error(f"[{request_id}] Falha ao ler PDF {filename}: {str(exc)}", exc_info=True)
            metadata_arquivos.append({
                "filename": filename,
                "status": "error",
                "motivo": "Falha na leitura interna da estrutura do PDF."
            })

    if not textos_processados:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nenhum dos currículos fornecidos continha texto válido para análise."
        )

    try:
        resultado_ia = await analisar_varios_candidatos(curriculos=textos_processados)

        elapsed_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            f"[{request_id}] Lote processado com sucesso",
            extra={"tempo_ms": elapsed_time_ms, "candidatos_analisados": len(textos_processados)}
        )

        return {
            "success": True,
            "request_id": request_id,
            "processing_time_ms": elapsed_time_ms,
            "summary": {
                "total_recebidos": len(files),
                "total_analisados": len(textos_processados),
                "arquivos": metadata_arquivos
            },
            "data": resultado_ia
        }

    except Exception as exc:
        logger.error(f"[{request_id}] Erro crítico no pipeline de IA: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha interna ao processar a Inteligência de Talentos."
        )