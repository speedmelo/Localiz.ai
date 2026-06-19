import pdfplumber

def extrair_texto_pdf(file):
    texto = ""

    with pdfplumber.open(file.file) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() or ""

    return textofrom typing import BinaryIO

import pdfplumber

from app.core.logging import get_logger

logger = get_logger("pdf_service")


MAX_PDF_PAGES = 20
MAX_TEXT_LENGTH = 60_000


def extrair_texto_pdf(file: BinaryIO) -> str:
    """
    Extrai texto de um PDF de forma segura para análise de currículo.
    """

    textos: list[str] = []

    try:
        with pdfplumber.open(file) as pdf:
            for index, pagina in enumerate(pdf.pages):
                if index >= MAX_PDF_PAGES:
                    break

                texto_pagina = pagina.extract_text() or ""

                if texto_pagina.strip():
                    textos.append(texto_pagina.strip())

        texto_final = "\n\n".join(textos).strip()

        if len(texto_final) > MAX_TEXT_LENGTH:
            texto_final = texto_final[:MAX_TEXT_LENGTH]

        return texto_final

    except Exception as exc:
        logger.exception("Erro ao extrair texto do PDF.")
        raise ValueError("Não foi possível extrair o texto do PDF.") from exc


async def extrair_texto_upload_pdf(upload_file) -> str:
    """
    Compatível com UploadFile do FastAPI.
    """

    if not upload_file.filename.lower().endswith(".pdf"):
        raise ValueError("O arquivo enviado precisa ser um PDF.")

    return extrair_texto_pdf(upload_file.file)
