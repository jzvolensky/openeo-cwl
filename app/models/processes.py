from pydantic import BaseModel, HttpUrl, Field # type: ignore
from typing import Optional, Dict, Any # type: ignore

class ExecutionUnit(BaseModel):
    href: str
    type: Optional[str] = Field(None, alias="type")

class Process(BaseModel):
    executionUnit: ExecutionUnit