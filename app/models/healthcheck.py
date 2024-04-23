from pydantic import BaseModel # type: ignore

class HealthCheck(BaseModel):
    status: str = "OK"