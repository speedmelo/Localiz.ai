# -*- coding: utf-8 -*-
import asyncio
import re
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


def extrair_linha_endereco(texto_completo: str) -> str:
    """
    Recebe o texto retornado do PDF e isola a linha de endereço
    focando em Rua, Bairro e Cidade, sem depender de CEP.
    """
    if not texto_completo:
        return "Endereço não encontrado"

    # 1. Busca por rótulos clássicos de endereço (ex: "Endereço: Rua da Servidão, 140...")
    match_rotulo = re.search(
        r'(?:endereço|endereco|localização|localizacao|residência|residencia):\s*(.*)', 
        texto_completo, 
        re.IGNORECASE
    )
    if match_rotulo:
        linha = match_rotulo.group(1).split('\n')[0].strip()
        if len(linha) > 5:
            logger.info(f"Endereço localizado via rótulo: {linha}")
            return linha

    # 2. Fallback: Procura por linhas com palavras de logradouro (Rua, Av, Servidão) + SP/Cidade
    padrao_logradouro = r'((?:rua|av|avenida|alameda|praça|rodovia|servidão|servidáo).*?(?:/|-)?\s*(?:sp|são paulo|sao paulo))'
    match_rua = re.search(padrao_logradouro, texto_completo, re.IGNORECASE)
    if match_rua:
        linha_rua = match_rua.group(1).strip()
        logger.info(f"Endereço localizado via padrão de logradouro: {linha_rua}")
        return linha_rua

    # 3. Terceiro fallback: Varre as linhas buscando nome da cidade com contexto
    for linha in texto_completo.split('\n'):
        if re.search(r'\b(amparo|campinas|são paulo|bragança|cotia|taboão|santos)\b', linha, re.IGNORECASE):
            if any(termo in linha.lower() for termo in ['rua', 'av', 'bairro', ' nº', 'nº', '-', 'servidão']):
                return linha.strip()

    logger.warning("Não foi possível identificar um endereço válido no texto extraído.")
    return "Endereço não identificado"