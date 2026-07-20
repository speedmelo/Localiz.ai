from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
import re
import os
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types

# 🔥 PASSO 6 - Tenta importar rotas modulares se existirem
try:
    from app.routes import match
    USE_ROUTES = True
except:
    USE_ROUTES = False

app = FastAPI()

# =========================
# CORS CONFIGURAÇÃO
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CONFIG GEMINI API
# =========================
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ==========================================
# 🛠️ MOTOR DE EXTRAÇÃO ROBUSTO (CEP & RUA)
# ==========================================
def extrair_localizacao_completa(texto_pdf: str) -> str:
    """
    Varre o texto do currículo procurando primeiro por um CEP válido.
    Se não encontrar, faz uma varredura semântica por endereços textuais (Rua, Av).
    """
    if not texto_pdf:
        return "Não Identificado"
        
    # Normaliza o texto removendo quebras de linha e espaços duplicados
    texto_limpo = " ".join(texto_pdf.split())
    
    # 1. TENTATIVA 1: Busca por CEP (Flexível com ou sem hífen/espaços)
    cep_match = re.search(r'\b\d{5}\s*-?\s*\d{3}\b', texto_limpo)
    if cep_match:
        cep_puro = re.sub(r'\D', '', cep_match.group(0))
        return f"CEP {cep_puro[:5]}-{cep_puro[5:]}"
    
    # 2. TENTATIVA 2: Busca por Endereço por Extenso (Logradouros comuns + Número)
    padrao_endereco = re.search(
        r'\b(Rua|R\.|Avenida|Av\.|Alameda|Al\.|Praça|Prç\.|Rodovia|Rod\.)\s+[^,.\n]+?,\s*\d+\b', 
        texto_limpo, 
        re.IGNORECASE
    )
    if padrao_endereco:
        endereco_encontrado = padrao_endereco.group(0)
        # Captura o contexto ao redor (até 80 caracteres) para não perder o Bairro/Cidade no Geocoding
        inicio_bloco = texto_limpo.find(endereco_encontrado)
        return texto_limpo[inicio_bloco:inicio_bloco + 80].strip()
        
    return "Não Identificado"

# =========================
# FUNÇÕES AUXILIARES JSON
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

# ==========================================
# 🚀 NOVA ROTA DE ATRAÇÃO DE TALENTOS (FRONTEND)
# ==========================================
@app.post("/candidates/upload-matching")
async def upload_matching(file: UploadFile = File(...)):
    try:
        # Tenta extrair usando o service padrão do projeto, senão faz o fallback
        try:
            from app.services.pdf_service import extrair_texto_pdf
            texto_pdf = extrair_texto_pdf(file)
        except:
            texto_pdf = file.file.read().decode("utf-8", errors="ignore")
        
        # Roda o motor robusto de localização
        localizacao = extrair_localizacao_completa(texto_pdf)
        
        # Simulação inteligente das regras de negócios das filiais (Perímetro Localiza)
        filiais_mock = [
            {
                "nome": "Localiza Aeroporto Congonhas",
                "regiao": "Capital",
                "sub_regiao": "Zona Sul",
                "distancia_km": 4.2
            },
            {
                "nome": "Localiza Centro - SP",
                "regiao": "Capital",
                "sub_regiao": "Centro",
                "distancia_km": 8.7
            }
        ]
        
        if localizacao == "Não Identificado":
            filiais_mock = []

        return {
            "cep_candidato": localizacao,
            "filiais_recomendadas": filiais_mock
        }

    except Exception as e:
        print("ERRO UPLOAD MATCHING:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no motor de matching: {str(e)}"
        )

# ==========================================
# 🧠 IA PRINCIPAL: ANÁLISE COMPLETA (LEGADA)
# ==========================================
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
# ENDPOINT MATCH INTELIGENTE
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
# INCLUSÃO DE ROTAS
# =========================
if USE_ROUTES:
    app.include_router(match.router)

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "Descomplic.AI RH rodando 🚀"}