from __future__ import annotations

import os
import sys
from pathlib import Path


def esta_empacotado() -> bool:
    return bool(getattr(sys, "frozen", False))


def pasta_embutida() -> Path:
    if esta_empacotado():
        base = getattr(sys, "_MEIPASS", None)
        if base:
            return Path(base)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def pasta_base() -> Path:
    if esta_empacotado():
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return Path(local) / "CorretorSINTEGRA"
        return Path.home() / "CorretorSINTEGRA"
    return Path(__file__).resolve().parent.parent


def pasta_pacote() -> Path:
    if esta_empacotado():
        return pasta_base() / "corretor_sintegra"
    return Path(__file__).resolve().parent


def pasta_dados() -> Path:
    if esta_empacotado():
        return pasta_base() / "dados"
    return Path(__file__).resolve().parent.parent / "data"
