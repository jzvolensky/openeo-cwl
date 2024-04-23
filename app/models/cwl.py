from pydantic import BaseModel, Field # type: ignore
from typing import Dict, Any

class CWL(BaseModel):
    filename: str = Field(..., title="The filename of the CWL file", example="convert-url-app.cwl")
    content: str 

class ExecutionRequest(BaseModel):
    filename: str = Field(..., title="The filename of the CWL file", example="convert-url-app.cwl")
    yaml_filename: str = Field(..., title="The filename of the YAML file", example="/parameters/convert-url-app.yaml")
    workflow_id: str = Field(..., title="The ID of the workflow", example="convert")
    inputs: Dict[str, Any] = Field(..., title="The inputs of the workflow", example={"fn": "resize", "url": "https://eoepca.org/media_portal/images/logo6_med.original.png", "size": "50%"})
    

