# app_web.py
from pathlib import Path
from tempfile import mkdtemp
from flask import (
    Flask, render_template, request, redirect,
    url_for, send_file, flash,
)

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

    if request.method == "POST":
        # handle file upload
        f = request.files.get("json_file")
        if not f or not f.filename.lower().endswith(".json"):
            flash("Please choose a .json file")
            return redirect(request.url)
        filename = f.filename
        save_path = UPLOAD_DIR / filename
        f.save(save_path)
    else:
        # when coming via redirect with ?filename=…
        filename = request.args.get("filename")

    # always list all tiles — so your table rows always render
    tiles = list_tiles()

    return render_template(
        "select.html",
        filename=filename,
        tiles=tiles,
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
