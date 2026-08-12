from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .models import CorretorPlugin


def _carregar_modulo(caminho: Path):
    nome = "plugin_" + caminho.stem.replace("-", "_")
    spec = importlib.util.spec_from_file_location(nome, caminho)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível criar spec para {caminho.name}")
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


class PluginManager:
    def __init__(self, pasta: Path, pastas_extra: Optional[List[Path]] = None):
        self.pasta = pasta
        self.pastas_extra = pastas_extra or []
        self.plugins: List[CorretorPlugin] = []
        self.avisos: List[str] = []

    def scan(self) -> List[CorretorPlugin]:
        self.plugins = []
        self.avisos = []
        raiz = str(self.pasta.parent)
        if raiz not in sys.path:
            sys.path.insert(0, raiz)

        por_id: Dict[str, CorretorPlugin] = {}
        pastas = [self.pasta] + list(self.pastas_extra)
        for pasta in pastas:
            if not pasta.exists():
                self.avisos.append(f"Pasta de corretores não encontrada: {pasta}")
                continue
            for caminho in sorted(pasta.glob("*.py")):
                if caminho.name == "__init__.py":
                    continue
                plugin = self._carregar(caminho)
                if plugin is not None:
                    por_id[plugin.id] = plugin
        self.plugins = list(por_id.values())
        return self.plugins

    def _carregar(self, caminho: Path) -> Optional[CorretorPlugin]:
        try:
            modulo = _carregar_modulo(caminho)
        except Exception as exc:
            self.avisos.append(f"{caminho.name}: falha ao importar ({exc})")
            return None
        plugin = getattr(modulo, "plugin", None)
        if plugin is None:
            self.avisos.append(f"{caminho.name}: objeto 'plugin' não encontrado")
            return None
        if not isinstance(plugin, CorretorPlugin):
            self.avisos.append(f"{caminho.name}: objeto 'plugin' do tipo inválido")
            return None
        return plugin
