from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.dependencies import require_role
from app.models.user import User

from app.services.llm_service import (
    generate_answer,
    LLMServiceError
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ConnectionTestRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=1000
    )


@router.post("/connection-test")
def test_gapgpt_connection(
    payload: ConnectionTestRequest,
    current_user: User = Depends(require_role("admin"))
):
    try:
        answer = generate_answer([
            {
                "role": "user",
                "content": payload.prompt
            }
        ])

        return {
            "status": "success",
            "provider": "GapGPT",
            "answer": answer
        }

    except LLMServiceError:
        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed."
        )