"""Ejecuta células en orden mediante IPython en proceso, sin abrir puertos.

Alternativa a nbclient para entornos que no permiten iniciar un kernel TCP.
Captura stdout, tablas HTML y figuras PNG reales; no simula resultados.
"""

import base64
import io
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.display import display
from IPython.utils.capture import capture_output

BASE = Path(__file__).resolve().parents[1]
os.chdir(BASE)
target = BASE / "notebooks/investigacion_multimodal.ipynb"
notebook = nbformat.read(target, as_version=4)
shell = InteractiveShell.instance()


def png_bytes(figure):
    stream = io.BytesIO()
    figure.savefig(stream, format="png", dpi=110, bbox_inches="tight")
    return stream.getvalue()


shell.display_formatter.formatters["image/png"].for_type(Figure, png_bytes)


def show_figures(*args, **kwargs):
    for number in plt.get_fignums():
        figure = plt.figure(number)
        display(figure)
        plt.close(figure)


plt.show = show_figures
count = 0
for cell in notebook.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    with capture_output(stdout=True, stderr=True, display=True) as captured:
        execution = shell.run_cell(cell.source, store_history=False)
    error = execution.error_before_exec or execution.error_in_exec
    if error:
        raise RuntimeError(f"Error en célula {count}: {error}") from error
    cell.execution_count = count
    cell.outputs = []
    if captured.stdout:
        cell.outputs.append(nbformat.v4.new_output("stream", name="stdout", text=captured.stdout))
    if captured.stderr:
        cell.outputs.append(nbformat.v4.new_output("stream", name="stderr", text=captured.stderr))
    for rich in captured.outputs:
        data = dict(rich.data)
        for mimetype, value in list(data.items()):
            if isinstance(value, bytes):
                data[mimetype] = base64.b64encode(value).decode("ascii")
        cell.outputs.append(nbformat.v4.new_output("display_data", data=data, metadata=rich.metadata))
notebook.metadata["execution"] = {"method": "IPython in-process, top-to-bottom", "executed_at": datetime.now(timezone.utc).isoformat(), "code_cells_executed": count, "reason": "Portable executor without TCP kernel requirement"}
nbformat.validate(notebook)
nbformat.write(notebook, target)
from nbconvert import HTMLExporter
exporter = HTMLExporter()
html, _ = exporter.from_notebook_node(notebook)
target.with_suffix(".html").write_text(html, encoding="utf-8")
print(f"Ejecutadas {count} células; outputs {sum(len(cell.get('outputs', [])) for cell in notebook.cells)}")
