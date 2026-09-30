"""Comic Exporter: PDF via FPDF (fpdf2)."""
import os
from fpdf import FPDF


def _latin1(text: str) -> str:
    """FPDF core fonts only support latin-1; replace fancy punctuation."""
    table = {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-", "\u2014": "-", "\u2026": "..."}
    for k, v in table.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


def export_pdf(comic: dict, comic_dir: str, out_path: str) -> str:
    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    for page_name in comic["pages"]:
        pdf.add_page()
        pdf.image(os.path.join(comic_dir, page_name), x=0, y=0, w=210, h=297)

    # story narration page(s)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, _latin1(comic["title"]), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(4)
    pdf.multi_cell(0, 7, _latin1(comic["narration"]))

    pdf.output(out_path)
    return out_path
