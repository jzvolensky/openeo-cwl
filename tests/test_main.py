from fastapi.testclient import TestClient # type: ignore
from app.main import app # type: ignore
from app.models.processes import Process # type: ignore

client = TestClient(app)

def test_create_process():
    process = Process(executionUnit={
        "href": "https://raw.githubusercontent.com/EOEPCA/convert/main/convert-url-app.cwl",
        "type": "application/cwl"
    })

    response = client.post("/processes", json=process.dict())

    assert response.status_code == 200
    assert response.json() == {"filename": "convert-url-app.cwl"}