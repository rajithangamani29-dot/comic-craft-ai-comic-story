"""Layout Builder: arranges panel images + captions into comic pages (2x2 grid, A4 @150dpi)."""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1240, 1754
MARGIN = 40
HEADER_H = 100
CAPTION_H = 130
PANELS_PER_PAGE = 4
CELL_W = (PAGE_W - 3 * MARGIN) // 2  # 560


def _font(size):
    for name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_pages(title: str, panels: list, out_dir: str) -> list:
    """Reads panel_N.png from out_dir, writes page_N.png, returns list of page file names."""
    pages = []
    for start in range(0, len(panels), PANELS_PER_PAGE):
        chunk = panels[start:start + PANELS_PER_PAGE]
        page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
        d = ImageDraw.Draw(page)
        d.rectangle([0, 0, PAGE_W, HEADER_H - 20], fill=(13, 148, 136))
        d.text((MARGIN, 22), title, fill="white", font=_font(40))

        for j, panel in enumerate(chunk):
            idx = start + j
            col, row = j % 2, j // 2
            x = MARGIN + col * (CELL_W + MARGIN)
            y = HEADER_H + MARGIN + row * (CELL_W + CAPTION_H + MARGIN)

            img = Image.open(os.path.join(out_dir, f"panel_{idx + 1}.png")).convert("RGB")
            img = img.resize((CELL_W, CELL_W))
            page.paste(img, (x, y))
            d.rectangle([x, y, x + CELL_W, y + CELL_W], outline="black", width=4)

            # caption box
            cy = y + CELL_W
            d.rectangle([x, cy, x + CELL_W, cy + CAPTION_H], fill=(255, 251, 219), outline="black", width=4)
            text = panel.get("dialogue", "")
            ty = cy + 12
            for line in textwrap.wrap(text, 40)[:4]:
                d.text((x + 14, ty), line, fill="black", font=_font(24))
                ty += 30

        name = f"page_{len(pages) + 1}.png"
        page.save(os.path.join(out_dir, name))
        pages.append(name)
    return pages
