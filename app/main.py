import os
from typing import Optional

from models.healthcheck import HealthCheck
from db.database import session, CWL

import httpx  # type: ignore
import requests # type: ignore
from fastapi import FastAPI, APIRouter, UploadFile, status, HTTPException, File, Form  # type: ignore
from fastapi.responses import JSONResponse, RedirectResponse  # type: ignore
from cwltool.context import LoadingContext  # type: ignore
from cwltool.load_tool import load_tool  # type: ignore
from sqlalchemy.exc import OperationalError  # type: ignore

router = APIRouter()

app = FastAPI()

@router.get("/", tags=["Landing Page"])
async def landing_page():
    return {
        "links": [
            {
                "rel": "service-desc",
                "href": "/ogc-api/openapi.json",
                "type": "application/json",
            },
            {
                "rel": "conformance",
                "href": "/ogc-api/conformance",
                "type": "application/json",
            },
            {
                "rel": "processes",
                "href": "/ogc-api/processes",
                "type": "application/json",
            },
        ]
    }


@router.post(
    "/ogc-api/processes",
    tags=["processes"],
    summary="OGC API processes endpoint",
    response_description="Return the filename of the process",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def upload_cwl(url: str, workflow_id: str, name: Optional[str] = None):
    try:
        response = requests.get(url)
        response.raise_for_status()

        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'app', 'CWL_FILES')
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, name if name else url.split('/')[-1])
        with open(file_path, "wb") as buffer:
            buffer.write(response.content)

        if session.query(CWL).filter_by(name=name if name else url.split('/')[-1]).first() is not None:
            raise HTTPException(
                status_code=400,
                detail="Name is already in use. Please choose a different name.",
            )
        
        new_cwl = CWL(name=name if name else url.split('/')[-1], workflow_id=workflow_id)
        session.add(new_cwl)
        session.commit()

        return {"status": "success"}
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@router.get("/ogc-api/processes", tags=["processes"])
async def list_processes_db():
    try:
        cwls = session.query(CWL).all()

        print("CWLs:", cwls)

        return {"processes": [cwl.to_dict() for cwl in cwls]}
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database is not available.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ogc-api/processes/", tags=["processes"])
async def delete_process(filename: str):
    try:
        os.remove(f"./CWL_FILES/{filename}")
        return {"message": "File {filename} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/ogc-api/execute",
    tags=["execute"],
    summary="OGC API execute endpoint",
    response_description="Return the execution result",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
@router.get("/ogc-api/conformance", tags=["Conformance"])
async def conformance():
    return {
        "conformsTo": [
            "http://www.opengis.net/spec/ogcapi-processes-1/0.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-processes-1/0.0/conf/json",
        ]
    }


@router.get("/ogc-api/openapi.json", tags=["API Definition"])
async def api_definition():
    return RedirectResponse(url="/openapi.json")


@router.get("/healthcheck", tags=["healthcheck"])
async def healthcheck():
    async with httpx.AsyncClient() as client:
        for endpoint in ["/", "/ogc-api/conformance", "/ogc-api/processes"]:
            try:
                response = await client.get(f"http://localhost:8000{endpoint}")
                response.raise_for_status()
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                return JSONResponse(
                    status_code=500, content={"status": "Error", "detail": str(e)}
                )
    return HealthCheck(status="OK")


app.include_router(router)