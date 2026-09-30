"""FastAPI Backend (app/main.py)"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router

app = FastAPI(title="ComicCraft - AI Comic Story Creator")
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
app.include_router(router)
