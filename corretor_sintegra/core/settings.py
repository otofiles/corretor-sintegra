from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .models import MODO_AUTO_RELATAR, MODOS


class Settings:
    def __init__(self, caminho: Path):
        self.caminho = caminho
        self.backup: bool = True
        self.exibir_relatorio_tecnico: bool = False
        self.plugins: Dict[str, Dict[str, object]] = {}

    def carregar(self, plugins: List) -> None:
        dados = {}
        if self.caminho.exists():
            try:
                dados = json.loads(self.caminho.read_text(encoding="utf-8"))
            except Exception:
                dados = {}
        self.backup = bool(dados.get("backup", True))
        self.exibir_relatorio_tecnico = bool(dados.get("exibir_relatorio_tecnico", False))
        salvos = dados.get("plugins", {})
        if not isinstance(salvos, dict):
            salvos = {}
        self.plugins = {}
        for p in plugins:
            cfg = salvos.get(p.id, {})
            if not isinstance(cfg, dict):
                cfg = {}
            modo = cfg.get("modo", MODO_AUTO_RELATAR)
            if modo not in MODOS:
                modo = MODO_AUTO_RELATAR
            self.plugins[p.id] = {
                "habilitado": bool(cfg.get("habilitado", True)),
                "modo": modo,
            }

    def salvar(self) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        dados = {
            "backup": self.backup,
            "exibir_relatorio_tecnico": self.exibir_relatorio_tecnico,
            "plugins": self.plugins,
        }
        self.caminho.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
        )
