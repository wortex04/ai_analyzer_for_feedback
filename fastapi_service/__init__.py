from fastapi import FastAPI

from fastapi_service.api.v1 import telegram_api
from fastapi_service.api.v2 import streamlit_api
from fastapi_service.settings.default import settings

app = FastAPI(
    title=settings.project.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)


@app.get("/")
async def root():
    return {"message": "good"}


@app.on_event("startup")
async def startup():
    pass


app.include_router(telegram_api.router, prefix="/api/v1/telegram_api", tags=["ml/dl"])
app.include_router(streamlit_api.router, prefix="/api/v2/streamlit", tags=["ml/dl"])