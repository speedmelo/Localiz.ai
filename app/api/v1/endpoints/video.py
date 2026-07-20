from fastapi import APIRouter

router = APIRouter()

@router.get("/video-token")
def generate_video_token():
    return {
        "token": "GERAR_TOKEN_AQUI",
        "channel": "entrevista-123"
    }