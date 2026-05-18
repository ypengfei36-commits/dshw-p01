from __future__ import annotations

from pathlib import Path

import nbformat
from nbconvert import HTMLExporter


ROOT = Path(__file__).resolve().parents[1]
nb = nbformat.read(ROOT / "03_analysis.ipynb", as_version=4)
html, _ = HTMLExporter().from_notebook_node(nb)
(ROOT / "report.html").write_text(html, encoding="utf-8")
print("Wrote report.html")
