"""
Public, non-interactive entry points for web apps or scheduled jobs.

Nothing in here should ever call prompt_toolkit, input(), or rich.Console.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

from .src.funcs import JSONDataExtractor, DataFrameCompilation

# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------

def _make_compiler(json_path: Path) -> DataFrameCompilation:
    extractor = JSONDataExtractor(json_path)
    return DataFrameCompilation(extractor)


# ToolkitExtractionWeb/eefdata/api.py
from inspect import ismethod

def _tile_map(compiler: DataFrameCompilation) -> dict[int, callable]:
    """Return {id: bound_method} – omit tiles that aren't implemented."""
    mapping = {
        1: 'make_dataframe_1',
        2: 'make_dataframe_2',
        3: 'make_dataframe_3',
        4: 'make_dataframe_4',
        5: 'make_dataframe_5',
        6: 'make_dataframe_6',
        7: 'make_dataframe_7',
        8: 'make_dataframe_8',
        9: 'make_dataframe_9',
        10: 'make_dataframe_10'

    }
    return {
        i: getattr(compiler, attr)
        for i, attr in mapping.items()
        if ismethod(getattr(compiler, attr, None))
    }   


# ----------------------------------------------------------------------
# public API
# ----------------------------------------------------------------------

# --- keep the imports you already have ------------------------------------
from inspect import isfunction        # add this next to your other imports
# --------------------------------------------------------------------------

def list_tiles() -> dict[int, str]:
    """
    Return {id: label} for every make_dataframe_N *implemented* on the
    DataFrameCompilation class – no JSON extractors, no I/O.
    """
    labels = {
        1: "Dataframe 1",
        2: "Dataframe 2",
        3: "Sample Size",
        4: "Effect Size A",
        5: "Effect Size B",
        6: "Data Analysis",
        7: "Outcome Data",
        8: "Study Security",
        9: "Padlocks",
        10: "References"

    }

    # ------------------------------------------------------------
    # look at the *class* (not an instance) to see what's defined
    # ------------------------------------------------------------
    mapping = {
        1: "make_dataframe_1",
        2: "make_dataframe_2",
        3: "make_dataframe_3",
        4: "make_dataframe_4",
        5: "make_dataframe_5",
        6: "make_dataframe_6",
        7: "make_dataframe_7",
        8: "make_dataframe_8",
        9: "make_dataframe_9",
        10: "make_dataframe_10"

   }

    implemented = {
        i for i, attr in mapping.items()
        if isfunction(getattr(DataFrameCompilation, attr, None))
    }

    return {i: labels[i] for i in sorted(implemented)}



import inspect   # ← add at top of api.py if it isn’t imported yet
from pathlib import Path

# --------------------------------------------------------------------------
# create_csv  – add **extras and forward only recognised parameters
# --------------------------------------------------------------------------
import inspect

def create_csv(
    json_path: str | Path,
    tile_id: int,
    *,
    output_dir: str | Path | None = None,
    **extras,                          # <-- anything else (e.g. strand='…')
) -> Path:
    ...
    compiler = _make_compiler(json_path)
    fn = _tile_map(compiler).get(tile_id)
    if fn is None:
        raise ValueError(f"Tile {tile_id} not implemented")

    # build kwargs accepted by *this* make_dataframe_N
    sig = inspect.signature(fn).parameters
    kwargs = {"save_file": True, "clean_cols": False}
    if "output_dir" in sig: kwargs["output_dir"] = output_dir
    for k, v in extras.items():
        if k in sig: kwargs[k] = v       # only pass names the method expects

    _df, csv_path = fn(**kwargs)         # every tile method returns (df, path)
    return Path(csv_path)


