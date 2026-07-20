from fastapi import APIRouter

router = APIRouter()

@router.post("/agendar")
def agendar_entrevista(data: dict):
    return {
        "status": "agendado",
        "dados": data
    }