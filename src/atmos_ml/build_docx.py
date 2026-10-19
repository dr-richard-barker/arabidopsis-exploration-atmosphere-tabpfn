"""
Compiles the publication-ready Markdown manuscript
(manuscript_exploration_atmosphere_tabpfn.md) into a richly formatted Word
document (manuscript_exploration_atmosphere_tabpfn.docx) with embedded 300 DPI
figures and formatted tables using python-docx.
"""
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

WORKSPACE = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156")
PROJECT_DIR = WORKSPACE / "arabidopsis_exploration_atmosphere"
MD_PATH = PROJECT_DIR / "manuscript" / "manuscript_exploration_atmosphere_tabpfn.md"
DOCX_PATH = PROJECT_DIR / "manuscript" / "manuscript_exploration_atmosphere_tabpfn.docx"
FIG_DIR = PROJECT_DIR / "manuscript" / "figures"


def _add_formatted_runs(paragraph, text: str) -> None:
    """Parse **bold**, *italic*, and `code` inline markdown into docx runs."""
    # Clean LaTeX inline math markers for clean Word typography
    cleaned = text.replace("\\text{", "").replace("\\textbf{", "")
    cleaned = cleaned.replace("\\Delta", "Δ").replace("\\log_2", "log2").replace("\\mu", "μ")
    cleaned = cleaned.replace("\\pm", "±").replace("\\times", "×").replace("\\le", "≤").replace("\\ge", "≥")
    cleaned = cleaned.replace("\\propto", "∝").replace("\\approx", "≈").replace("\\rho", "ρ")
    cleaned = cleaned.replace("\\beta", "β").replace("\\varepsilon", "ε").replace("\\phi", "φ")
    cleaned = cleaned.replace("\\delta^{13}C", "δ13C").replace("\\textperthousand", "‰")
    cleaned = re.sub(r"\$([^$]+)\$", r"\1", cleaned)

    tokens = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", cleaned)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            run = paragraph.add_run(tok[2:-2])
            run.bold = True
        elif tok.startswith("*") and tok.endswith("*"):
            run = paragraph.add_run(tok[1:-1])
            run.italic = True
        elif tok.startswith("`") and tok.endswith("`"):
            run = paragraph.add_run(tok[1:-1])
            run.font.name = "Courier New"
            run.font.size = Pt(9.5)
        else:
            paragraph.add_run(tok)


def build_docx() -> None:
    doc = Document()

    # Configure normal style
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    lines = MD_PATH.read_text().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line or line.strip() == "---":
            i += 1
            continue

        # Headings
        if line.startswith("# "):
            h = doc.add_heading(level=0)
            _add_formatted_runs(h, line[2:].strip())
            i += 1
            continue
        if line.startswith("## "):
            h = doc.add_heading(level=1)
            _add_formatted_runs(h, line[3:].strip())
            i += 1
            continue
        if line.startswith("### "):
            h = doc.add_heading(level=2)
            _add_formatted_runs(h, line[4:].strip())
            i += 1
            continue

        # Image embedding: ![alt](filename.png)
        img_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if img_match:
            img_file = img_match.group(2).strip()
            img_path = FIG_DIR / Path(img_file).name
            if img_path.exists():
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(str(img_path), width=Inches(6.3))
            i += 1
            continue

        # Display equation block $$...$$
        if line.strip().startswith("$$") and line.strip().endswith("$$"):
            eq_text = line.strip()[2:-2].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _add_formatted_runs(p, eq_text)
            i += 1
            continue

        # Markdown Table
        if line.strip().startswith("|") and line.strip().endswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                row_str = lines[i].strip()
                # Skip separator row | :--- | :---: |
                if not re.match(r"^\|[\s:\-\|]+\|$", row_str):
                    cells = [c.strip() for c in row_str.strip("|").split("|")]
                    table_lines.append(cells)
                i += 1
            if table_lines:
                n_rows = len(table_lines)
                n_cols = max(len(r) for r in table_lines)
                tbl = doc.add_table(rows=n_rows, cols=n_cols)
                tbl.style = "Table Grid"
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                for r_idx, row_cells in enumerate(table_lines):
                    for c_idx, cell_val in enumerate(row_cells):
                        if c_idx < n_cols:
                            cell_p = tbl.cell(r_idx, c_idx).paragraphs[0]
                            _add_formatted_runs(cell_p, cell_val)
                            for run in cell_p.runs:
                                run.font.size = Pt(8.5)
                                if r_idx == 0:
                                    run.bold = True
                doc.add_paragraph()
            continue

        # Bulleted or numbered list items
        if re.match(r"^\s*[-*]\s+", line):
            bullet_text = re.sub(r"^\s*[-*]\s+", "", line)
            p = doc.add_paragraph(style="List Bullet")
            _add_formatted_runs(p, bullet_text)
            i += 1
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            num_text = re.sub(r"^\s*\d+\.\s+", "", line)
            p = doc.add_paragraph(style="List Number")
            _add_formatted_runs(p, num_text)
            i += 1
            continue

        # Standard paragraph
        p = doc.add_paragraph()
        _add_formatted_runs(p, line)
        i += 1

    doc.save(str(DOCX_PATH))
    print(f"Successfully generated Word manuscript: {DOCX_PATH} ({DOCX_PATH.stat().st_size / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    build_docx()
