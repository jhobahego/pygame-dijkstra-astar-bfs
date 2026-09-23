"""Core purity: nothing under core/ may import pygame (in any form)."""

import re
from pathlib import Path

_PYGAME_IMPORT = re.compile(r"^\s*(import\s+pygame\b|from\s+pygame\b)", re.MULTILINE)


def test_core_does_not_import_pygame() -> None:
    modules = sorted(Path("core").rglob("*.py"))
    assert modules, "no se encontraron modulos bajo core/"
    offenders = [
        path
        for path in modules
        if _PYGAME_IMPORT.search(path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"core/ importa pygame en: {offenders}"
