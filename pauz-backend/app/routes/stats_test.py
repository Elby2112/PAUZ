from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_stats_endpoint():
    """
    Simple test endpoint to verify stats router is working
    """
    return {"message": "Stats endpoint is working", "status": "ok"}