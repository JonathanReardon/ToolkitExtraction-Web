# app_web.py
from pathlib import Path
from tempfile import mkdtemp
from flask import (
    Flask, render_template, request, redirect,
    url_for, send_file, flash
)

from eefdata.src.funcs import JSONDataExtractor, DataFrameCompilation
import json

from eefdata.api import create_csv, list_tiles

app = Flask(__name__)
app.secret_key = "replace-me"
UPLOAD_DIR = Path(mkdtemp())

# helper to invoke your API and forward the strand arg for tile 6
def run_tile(json_path: Path, tile_id: int, *, strand: str | None = None) -> Path:
    kwargs: dict[str, str] = {}
    if tile_id == 6 and strand:
        kwargs["strand"] = strand
    return create_csv(json_path, tile_id, output_dir=Path(mkdtemp()), **kwargs)

# -------------------------------------------------------
# Combined “index” + “select” into one route
# -------------------------------------------------------
@app.route("/select", methods=["GET", "POST"])
def select_page():
    filename = None
    df1_row_count = None

    if request.method == "POST":
        f = request.files.get("json_file")
        if not f or not f.filename.lower().endswith(".json"):
            flash("Please choose a .json file")
            return redirect(request.url)

        filename = f.filename
        file_bytes = f.read()

        # Save uploaded JSON to disk first
        save_path = UPLOAD_DIR / filename
        with open(save_path, 'wb') as out_file:
            out_file.write(file_bytes)

        # Then pass file path to extractor and compile dataframe
        extractor = JSONDataExtractor(json_path=save_path)
        compiler = DataFrameCompilation(extractor)
        df1, _ = compiler.make_dataframe_1(save_file=False)

        # Get row count for the template
        df1_row_count = len(df1)

    else:
        filename = request.args.get("filename")

    tiles = list_tiles()

    return render_template(
        "select.html",
        filename=filename,
        tiles=tiles,
        df1_row_count=df1_row_count,
    )



@app.route("/download/<filename>/<int:tile_id>")
def download(filename, tile_id):
    json_path = UPLOAD_DIR / filename
    if not json_path.exists():
        flash("Upload expired, start again")
        return redirect(url_for("select_page"))

    strand = request.args.get("strand")
    try:
        csv_path = run_tile(json_path, tile_id, strand=strand)
    except Exception as exc:
        flash(f"EEF export failed: {exc}")
        return redirect(url_for("select_page"))

    return send_file(csv_path, as_attachment=True, download_name=csv_path.name)

@app.route("/details/<int:tile_id>")
@app.route("/details/<int:tile_id>/<strand>")
def details(tile_id, strand=None):
    return render_template("details.html", tile_id=tile_id, strand=strand)

# redirect root → select
@app.route("/", methods=["GET"])
def index_redir():
    return redirect(url_for("select_page"))
