"""AI Comic Generation Logic (routes.py + Gemini + Diffusers)"""
import json
import uuid
from pathlib import Path
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

from . import gemini_service, image_generator, layout_builder, exporters

BASE = Path(__file__).parent
GEN_DIR = BASE / "static" / "generated"
EXPORT_DIR = BASE / "exports"
templates = Jinja2Templates(directory=str(BASE / "templates"))
router = APIRouter()


def _load_comic(comic_id: str) -> dict:
    path = GEN_DIR / comic_id / "comic.json"
    if not comic_id.isalnum() or not path.exists():
        raise HTTPException(404, "Comic not found")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"error": None})


@router.post("/generate")
def generate(
    request: Request,
    title: str = Form(...),
    idea: str = Form(...),
    genre: str = Form("Adventure"),
    style: str = Form("colorful cartoon"),
    characters: str = Form(""),
    panels: int = Form(4),
):
    panels = max(2, min(panels, 8))
    comic_id = uuid.uuid4().hex[:10]
    comic_dir = GEN_DIR / comic_id
    comic_dir.mkdir(parents=True)

    try:
        outline = gemini_service.generate_outline(title, idea, genre, style, characters, panels)  # Flash
        narration = gemini_service.generate_narration(outline, genre)                             # Pro
        used_placeholder = image_generator.generate_panel_images(outline["panels"], style, str(comic_dir))  # Diffusers
        pages = layout_builder.build_pages(outline["title"], outline["panels"], str(comic_dir))
    except Exception as e:
        return templates.TemplateResponse(
            request, "index.html", {"error": f"Generation failed: {e}"}, status_code=502
        )

    comic = {
        "id": comic_id,
        "title": outline["title"],
        "panels": outline["panels"],
        "narration": narration,
        "pages": pages,
        "used_placeholder": used_placeholder,
    }
    (comic_dir / "comic.json").write_text(json.dumps(comic, indent=2), encoding="utf-8")
    return RedirectResponse(f"/comic/{comic_id}", status_code=303)


@router.get("/comic/{comic_id}")
def preview(request: Request, comic_id: str):
    return templates.TemplateResponse(request, "comic_preview.html", {"comic": _load_comic(comic_id)})


@router.post("/export/{comic_id}")
def export(request: Request, comic_id: str):
    comic = _load_comic(comic_id)
    EXPORT_DIR.mkdir(exist_ok=True)
    out = EXPORT_DIR / f"{comic_id}.pdf"
    exporters.export_pdf(comic, str(GEN_DIR / comic_id), str(out))
    return templates.TemplateResponse(request, "export_success.html", {"comic": comic})


@router.get("/download/{comic_id}")
def download(comic_id: str):
    comic = _load_comic(comic_id)
    path = EXPORT_DIR / f"{comic_id}.pdf"
    if not path.exists():
        raise HTTPException(404, "Export the comic first")
    return FileResponse(path, media_type="application/pdf", filename=f"{comic['title']}.pdf")
