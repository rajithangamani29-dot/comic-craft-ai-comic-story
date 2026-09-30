"""Gemini AI Services
- Gemini Flash -> Comic outline (panel-wise scenes, dialogue, image prompts)
- Gemini Pro   -> Full story narration
"""
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

FLASH_MODEL = os.getenv("FLASH_MODEL", "gemini-2.5-flash")
PRO_MODEL = os.getenv("PRO_MODEL", "gemini-2.5-pro")


def _clean_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    return json.loads(text)


def generate_outline(title, idea, genre, style, characters, num_panels) -> dict:
    """Gemini Flash: returns {"title": str, "panels": [{scene, dialogue, image_prompt}]}"""
    prompt = f"""You are a comic book writer. Create a comic outline with exactly {num_panels} panels.
Title: {title}
Story idea: {idea}
Genre: {genre}
Art style: {style}
Characters: {characters or "invent suitable characters"}

Reply ONLY with JSON in this shape:
{{"title": "...", "panels": [
  {{"scene": "one-sentence description of what happens",
    "dialogue": "short caption or speech (max 20 words)",
    "image_prompt": "detailed visual description for an image generator, no text in image"}}
]}}"""
    model = genai.GenerativeModel(
        FLASH_MODEL, generation_config={"response_mime_type": "application/json"}
    )
    data = _clean_json(model.generate_content(prompt).text)
    data["panels"] = data.get("panels", [])[:num_panels]
    if not data["panels"]:
        raise ValueError("Gemini returned an outline with no panels")
    return data


def generate_narration(outline: dict, genre: str) -> str:
    """Gemini Pro: full story narration based on the outline."""
    panels = "\n".join(
        f"{i}. {p['scene']} ({p['dialogue']})" for i, p in enumerate(outline["panels"], 1)
    )
    prompt = f"""Write a engaging {genre} short story narration (about 200-300 words) for a comic titled
"{outline['title']}". Follow these panels in order:
{panels}
Write plain prose only, no headings or markdown."""
    model = genai.GenerativeModel(PRO_MODEL)
    return model.generate_content(prompt).text.strip()
