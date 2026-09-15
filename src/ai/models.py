from typing import Any, Optional

from pydantic import BaseModel, Field


class StructuredGenerationRequest(BaseModel):
    system_prompt: str = Field(min_length=1)
    user_prompt: str = Field(min_length=1)
    schema_name: str = Field(min_length=1)
    json_schema: dict[str, Any]
    max_output_tokens: int = Field(default=1200, ge=64, le=32768)


class StructuredGenerationResult(BaseModel):
    provider: str
    model: str
    data: dict[str, Any]
    request_id: Optional[str] = None
    input_tokens: Optional[int] = Field(default=None, ge=0)
    output_tokens: Optional[int] = Field(default=None, ge=0)
    latency_ms: Optional[float] = Field(default=None, ge=0)
