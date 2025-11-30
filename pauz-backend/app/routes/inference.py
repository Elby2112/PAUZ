from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from app.services.inference_service import inference_service

router = APIRouter()

class InferenceRequest(BaseModel):
    prompt: str
    model: str = "openai/gpt-3.5-turbo"

@router.post("/")
def get_inference(
    request: InferenceRequest = Body(...)
):
    """
    Endpoint to demonstrate getting a completion from an external model
    via the SmartInference service.
    """
    result = inference_service.get_completion_with_smart_inference(
        prompt=request.prompt,
        model=request.model
    )
    return result
