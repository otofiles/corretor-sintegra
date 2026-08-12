from __future__ import annotations

import shutil
from pathlib import Path


def criar_backup(arquivo: Path) -> Path:
    destino = arquivo.with_name(arquivo.name + ".bak")
    shutil.copy2(arquivo, destino)
    return destino
