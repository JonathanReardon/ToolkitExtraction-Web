#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re‑implemented **app.py** for *eef‑data* (Path C)
=================================================

*   Delegates **all CSV generation** to the new, non‑interactive
    `eef_data.api.create_csv()` facade – no more `prompt_toolkit` or
    `rich.prompt.Prompt.ask` inside the core logic.
*   Keeps a **tiny** prompt‑driven wrapper so the package can still be
    used from a terminal, but it is now safe to import from Flask or
    unit tests because nothing blocks on `stdin`.
*   Option 11 (the old custom‑builder state‑machine) is **not ported** –
    it remains in the legacy CLI.  Add it here later once you expose a
    pure function for that workflow.

Run examples
------------
```bash
# menu‑driven (same as before, but lightweight)
python -m eef_data my_study.json

# non‑interactive, perfect for cron jobs
python -m eef_data my_study.json --tile 3 --out ./exports/
```
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

try:
    # Local import when running from source tree
    from .api import list_tiles, create_csv
except ImportError:  # pragma: no cover – fallback when installed as a package
    from eef_data.api import list_tiles, create_csv  # type: ignore


def _print_menu(console: Console, tiles: dict[int, str]) -> None:
    """Pretty Rich table of tile IDs → labels."""
    table = Table(title="EEF Toolkit – Available Data Tiles", show_lines=False)
    table.add_column("ID", style="bold cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    for _id, label in tiles.items():
        table.add_row(str(_id), label)
    table.add_row("0", "[dim]Exit[/]")

    console.print(table)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(
        prog="eef-data",
        description="Generate CSV extracts from an EEF Toolkit JSON export.",
    )
    parser.add_argument(
        "json_file",
        metavar="JSON",
        type=Path,
        help="Path to the EEF JSON export (e.g. study_123.json)",
    )
    parser.add_argument(
        "-t",
        "--tile",
        type=int,
        help="Tile ID to export directly (skip menu)",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="Directory where the CSV will be written (defaults to JSON's folder)",
    )

    args = parser.parse_args(argv)

    console = Console()
    json_path = args.json_file.expanduser().resolve()
    if not json_path.exists():
        console.print(f"[red]File not found:[/] {json_path}")
        sys.exit(1)

    tiles = list_tiles()

    # ----------------------- interactive fallback -----------------------
    if args.tile is None:
        _print_menu(console, tiles)
        try:
            tile_id = int(console.input("[bold]Select tile number[/]: "))
        except KeyboardInterrupt:
            console.print("\nAborted by user.")
            return
    else:
        tile_id = args.tile

    if tile_id == 0:
        return  # graceful exit

    if tile_id not in tiles:
        console.print(f"[red]Unknown tile:[/] {tile_id}")
        sys.exit(1)

    # --------------------------- CSV export ----------------------------
    csv_path = create_csv(json_path, tile_id, output_dir=args.out)
    console.print(
        f":open_file_folder:  CSV for '[bold]{tiles[tile_id]}[/]' "
        f"saved to [green]{csv_path}[/]"
    )


# ------------- end of ToolkitExtractionWeb/eefdata/app.py -------------

if __name__ == "__main__":
    main()                 # ← run the CLI, nothing else
