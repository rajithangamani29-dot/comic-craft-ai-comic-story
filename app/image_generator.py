"""Diffusers (Stable Diffusion) -> panel-wise image generation.
Falls back to simple placeholder panels if USE_PLACEHOLDER=1 or diffusers/torch are not installed."""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

SD_MODEL = os.getenv("SD_MODEL", "stable-diffusion-v1-5/stable-diffusion-v1-5")
SD_STEPS = int(os.getenv("SD_STEPS", "25"))
SIZE = 512
_pipe = None


def _load_pipeline():
    global _pipe
    if _pipe is None:
        import torch
        from diffusers import StableDiffusionPipeline

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        _pipe = StableDiffusionPipeline.from_pretrained(SD_MODEL, torch_dtype=dtype)
        _pipe = _pipe.to(device)
    return _pipe


def _font(size):
    for name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _placeholder(index: int, scene: str) -> Image.Image:
    palette = [(255, 214, 165), (202, 255, 191), (155, 246, 255), (189, 178, 255), (255, 198, 255), (253, 255, 182)]
    img = Image.new("RGB", (SIZE, SIZE), palette[index % len(palette)])
    d = ImageDraw.Draw(img)
    d.text((24, 20), f"Panel {index + 1}", fill=(40, 40, 40), font=_font(34))
    y = 90
    for line in textwrap.wrap(scene, 34)[:10]:
        d.text((24, y), line, fill=(40, 40, 40), font=_font(22))
        y += 30
    return img


def generate_panel_images(panels: list, style: str, out_dir: str) -> bool:
    """Saves panel_1.png ... in out_dir. Returns True if placeholders were used."""
    use_placeholder = os.getenv("USE_PLACEHOLDER", "0") == "1"
    pipe = None
    if not use_placeholder:
        try:
            pipe = _load_pipeline()
        except Exception as e:  # diffusers/torch missing or model download failed
            print(f"[image_generator] Stable Diffusion unavailable, using placeholders: {e}")
            use_placeholder = True

    for i, panel in enumerate(panels):
        path = os.path.join(out_dir, f"panel_{i + 1}.png")
        if pipe is not None:
            prompt = f"{panel['image_prompt']}, {style}, comic book panel, detailed, no text"
            image = pipe(
                prompt,
                negative_prompt="text, watermark, speech bubble, blurry, deformed",
                num_inference_steps=SD_STEPS,
                height=SIZE,
                width=SIZE,
            ).images[0]
        else:
            image = _placeholder(i, panel["scene"])
        image.save(path)
    return use_placeholder
