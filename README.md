# ComicCraft – AI Comic Story Creator using Gemini Models

Flow: Browser → FastAPI (app/main.py) → Jinja2 + CSS → index.html (input form)
→ AI Comic Generation Logic (routes.py + Gemini + Diffusers)
   - Gemini Flash  → comic outline
   - Gemini Pro    → full story narration
   - Diffusers (Stable Diffusion) → panel-wise images
→ Layout Builder (layout_builder.py) → Comic Exporter (exporters.py, PDF via FPDF)
→ comic_preview.html → export_success.html

## Run
```
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # Linux/Mac: cp .env.example .env   then add GEMINI_API_KEY
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

## Real Stable Diffusion images (optional, GPU recommended)
```
pip install -r requirements-diffusers.txt
```
then set `USE_PLACEHOLDER=0` in `.env`. First run downloads the model (~4 GB). On CPU each panel takes minutes.
Without this, simple coloured placeholder panels are used so the whole pipeline still works.

Free Gemini key: https://aistudio.google.com/app/apikey
