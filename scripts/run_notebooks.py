from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ["01_download.ipynb", "02_clean.ipynb", "03_analysis.ipynb"]


for name in NOTEBOOKS:
    path = ROOT / name
    print(f"Executing {name} ...")
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=900,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
        allow_errors=False,
    )
    client.execute()
    nbformat.write(nb, path)
    print(f"Finished {name}")
