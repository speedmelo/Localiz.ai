from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import re
import os
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types

# 🔥 NOVO IMPORT (PASSO 6)
try:
    from app.routes import match
    USE_ROUTES = True
except:
    USE_ROUTES = False

app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CONFIG GEMINI
# =========================
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# =========================
# FUNÇÃO AUXILIAR JSON
# =========================
def safe_json(texto):
    try:
        return json.loads(texto)
    except:
        try:
            json_str = re.search(r'\{.*\}', texto, re.DOTALL).group()
            return json.loads(json_str)
        except:
            return {
                "erro": "Falha ao interpretar JSON",
                "resposta_bruta": texto
            }

# =========================
# IA PRINCIPAL
# =========================
async def analisar_candidato(curriculo_texto, vagas):

    vagas_formatadas = "\n\n".join([
        f"VAGA: {v['nome']}\nDESCRIÇÃO:\n{v['descricao']}"
        for v in vagas
    ])

    prompt = f"""
Você é um especialista SÊNIOR em recrutamento e seleção.

Faça uma análise profunda, crítica e estratégica.

OBJETIVO:
- Identificar se o candidato deve ser contratado
- Encontrar inconsistências
- Escolher a melhor vaga
- Gerar perguntas inteligentes

RETORNE APENAS JSON:

{{
  "melhor_vaga": "",
  "score": 0,
  "aprovado": true,
  "nivel": "junior | pleno | senior",
  "risco_contratacao": "baixo | medio | alto",
  "ranking": [
    {{"vaga": "", "score": 0}}
  ],
  "pontos_fortes": [],
  "pontos_fracos": [],
  "red_flags": [],
  "justificativa": "",
  "motivo_reprovacao": "",
  "perguntas": {{
    "tecnicas": [],
    "comportamentais": [],
    "armadilha": []
  }}
}}

CANDIDATO:
{curriculo_texto}

VAGAS:
{vagas_formatadas}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3
        )
    )

    return safe_json(response.text)

# =========================
# ENDPOINT PRINCIPAL (LEGADO)
# =========================
@app.post("/match-inteligente")
async def match_inteligente(request: Request):
    try:
        body = await request.json()

        curriculo = body.get("curriculo")
        vagas = body.get("vagas")

        if not curriculo or not vagas:
            raise HTTPException(
                status_code=400,
                detail="Currículo e vagas são obrigatórios"
            )

        resultado = await analisar_candidato(curriculo, vagas)

        return {
            "status": "sucesso",
            "resultado": resultado
        }

    except Exception as e:
        print("ERRO:", str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno"
        )

# =========================
# 🔥 PASSO 6 - ROTAS MODULARES
# =========================
if USE_ROUTES:
    app.include_router(match.router)

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "Descomplic.AI RH rodando 🚀"}