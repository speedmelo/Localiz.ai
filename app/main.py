from fastapi import FastAPI, Depends, HTTPException, Request, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid
import asyncio

# ==========================================
# CORE
# ==========================================
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.websocket_manager import manager

# ==========================================
# ROUTERS CENTRALIZADO
# ==========================================
from app.api.v1.router import api_router

# ==========================================
# DEPENDENCIES
# ==========================================
from app.dependencies import get_ai_service
from app.services.ai_service import AIService

# ==========================================
# SCHEMAS
# ==========================================
from app.schemas.match_schema import MatchRequest, MatchResponse

# ==========================================
# LIFESPAN
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia inicialização e shutdown da aplicação"""
    configure_logging(level=logging.INFO, log_to_file=True)
    
    logger = get_logger()
    logger.info(
        "🚀 Localiz.ai Talent Intelligence iniciado",
        extra={
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION,
            "project": settings.PROJECT_NAME
        }
    )
    
    yield
    
    logger.info("🛑 Aplicação encerrada com limpeza de recursos")


# ==========================================
# APP CONFIGURATION
# ==========================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Plataforma de Inteligência de Talentos para Recrutamento RH - Localiz.ai",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[{"name": "Match IA", "description": "Análise inteligente de candidatos"}]
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# GLOBAL EXCEPTION HANDLERS
# ==========================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger = get_logger()
    logger.warning(f"HTTP {exc.status_code} - {exc.detail} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail, "path": request.url.path}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger = get_logger()
    logger.exception(f"Erro não tratado | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Erro interno no servidor"}
    )


# ==========================================
# WEBSOCKET
# ==========================================
@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str = "general"):
    await manager.connect(websocket, room=room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_to_room({"type": "echo", "message": data}, room)
    except Exception:
        manager.disconnect(websocket, room=room)


# ==========================================
# ROUTERS
# ==========================================
app.include_router(api_router, prefix="/api/v1")


# ==========================================
# MATCH INTELIGENTE (Endpoint Principal)
# ==========================================
@app.post(
    "/api/v1/match-inteligente",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Match IA"]
)
async def match_inteligente(
    payload: MatchRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    logger = get_logger()

    try:
        logger.info(f"[{request_id}] Iniciando análise de candidato", extra={"candidato_id": payload.candidato_id})

        resultado = await asyncio.wait_for(
            ai_service.analisar_candidato(
                curriculo=payload.curriculo,
                vagas=payload.vagas
            ),
            timeout=45.0  # Aumentado um pouco
        )

        processing_time = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(f"[{request_id}] Análise concluída com sucesso", extra={"processing_time_ms": processing_time})

        # Notificação em tempo real
        await manager.send_to_room({
            "type": "analysis_completed",
            "request_id": request_id,
            "status": "success",
            "processing_time_ms": processing_time
        }, room="analyses")

        return MatchResponse(
            success=True,
            data=resultado,
            processing_time_ms=processing_time,
            model_version=settings.MODEL_NAME,
            request_id=request_id
        )

    except asyncio.TimeoutError:
        logger.error(f"[{request_id}] Timeout na análise IA")
        raise HTTPException(status_code=408, detail="Tempo limite excedido na análise")

    except ValueError as e:
        logger.warning(f"[{request_id}] Erro de validação: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"[{request_id}] Erro inesperado", exc_info=True)
        raise HTTPException(status_code=500, detail="Falha ao processar análise com IA")


# ==========================================
# HEALTH CHECKS
# ==========================================
@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": "Localiz.ai RH",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "active_websockets": manager.get_all_connections()
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "🚀 Localiz.ai Talent Intelligence está online",
        "docs": "/docs",
        "health": "/health"
    }