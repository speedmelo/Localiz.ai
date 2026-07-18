# -*- coding: utf-8 -*-
import asyncio
from typing import Any
import pdfplumber
from app.core.logging import get_logger

logger = get_logger("pdf_service")

# Constantes de proteção de memória (Defensive Programming)
MAX_PDF_PAGES = 20
MAX_TEXT_LENGTH = 60_000


def extrair_texto_pdf(file_object: Any) -> str:
    """
    Core síncrono para extração de texto de um arquivo PDF (File-like object).
    Aplica limites defensivos de páginas e caracteres para evitar estouro de memória (DoS).
    """
    paginas_extraidas: list[str] = []

    try:
        with pdfplumber.open(file_object) as pdf:
            for index, pagina in enumerate(pdf.pages):
                if index >= MAX_PDF_PAGES:
                    logger.warning(f"PDF atingiu o limite máximo de {MAX_PDF_PAGES} páginas. Interrompendo leitura.")
                    break

                texto_pagina = pagina.extract_text()
                if texto_pagina and texto_pagina.strip():
                    paginas_extraidas.append(texto_pagina.strip())

        texto_final = "\n\n".join(paginas_extraidas).strip()

        if len(texto_final) > MAX_TEXT_LENGTH:
            logger.warning(f"Texto extraído superou {MAX_TEXT_LENGTH} caracteres. Aplicando truncamento.")
            texto_final = texto_final[:MAX_TEXT_LENGTH]

        return texto_final

    except Exception as exc:
        logger.exception("Erro crítico de parsing no pdfplumber.")
        raise ValueError("Falha ao processar a estrutura interna do arquivo PDF.") from exc


async def extrair_texto_upload_pdf(upload_file: Any) -> str:
    """
    Wrapper assíncrono compatível com UploadFile do FastAPI.
    Executa a leitura pesada do PDF em uma thread separada para não bloquear o event loop.
    """
    filename = getattr(upload_file, "filename", "")
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Assinatura de arquivo inválida. O arquivo enviado precisa ser um PDF.")

    # Pulo do gato Senior: pdfplumber é síncrono (I/O Bound). 
    # Usamos to_thread para rodar no pool do asyncio e manter a API com alta concorrência.
    return await asyncio.to_thread(extrair_texto_pdf, upload_file.file)