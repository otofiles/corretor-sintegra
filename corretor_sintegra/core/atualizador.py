from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Callable, Optional
from urllib.request import Request, urlopen

from core import caminhos
from core.versao import VERSAO

REPOSITORIO = "otofiles/corretor-sintegra"
NOME_ASSET = "corretor_sintegra.zip"
TEMPO_LIMITE = 30
AGENTE = {"User-Agent": "CorretorSINTEGRA"}


def url_api_latest() -> str:
    override = os.environ.get("CORRETOR_API_URL")
    if override:
        return override
    return f"https://api.github.com/repos/{REPOSITORIO}/releases/latest"


def _baixar(url: str) -> bytes:
    req = Request(url, headers=AGENTE)
    with urlopen(req, timeout=TEMPO_LIMITE) as resp:
        return resp.read()


def _comparar_versoes(a: str, b: str) -> int:
    pa = [int(x) for x in a.split(".") if x.isdigit()]
    pb = [int(x) for x in b.split(".") if x.isdigit()]
    for x, y in zip(pa, pb):
        if x != y:
            return 1 if x > y else -1
    return (len(pa) > len(pb)) - (len(pa) < len(pb))


class Atualizador:
    def versao_local(self) -> str:
        return VERSAO

    def versao_remota(self) -> Optional[str]:
        try:
            dados = json.loads(_baixar(url_api_latest()).decode("utf-8"))
        except Exception:
            return None
        tag = dados.get("tag_name", "")
        return tag.lstrip("vV") or None

    def ha_atualizacao(self, remota: Optional[str] = None) -> bool:
        if remota is None:
            remota = self.versao_remota()
        if not remota:
            return False
        return _comparar_versoes(remota, self.versao_local()) > 0

    def _url_asset(self) -> Optional[str]:
        try:
            dados = json.loads(_baixar(url_api_latest()).decode("utf-8"))
        except Exception:
            dados = {}
        for asset in dados.get("assets", []):
            if asset.get("name") == NOME_ASSET:
                return asset.get("browser_download_url")
        return os.environ.get("CORRETOR_ASSET_URL")

    def baixar_e_aplicar(
        self, progresso: Optional[Callable[[str], None]] = None
    ) -> bool:
        progresso = progresso or (lambda msg: None)
        url = os.environ.get("CORRETOR_ASSET_URL") or self._url_asset()
        if not url:
            raise RuntimeError("Pacote de atualização não encontrado no GitHub.")

        progresso("Baixando pacote de atualização...")
        conteudo = _baixar(url)

        base = caminhos.pasta_base()
        pacote = caminhos.pasta_pacote()
        tmp = base / "_tmp_atualizacao"
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir(parents=True, exist_ok=True)
        zip_path = tmp / NOME_ASSET
        zip_path.write_bytes(conteudo)

        progresso("Extraindo atualização...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp)

        novo = tmp / "corretor_sintegra"
        if not novo.exists():
            raise RuntimeError("Pacote de atualização com formato inválido.")

        if pacote.exists():
            shutil.rmtree(pacote)
        shutil.move(str(novo), str(pacote))

        remota = self.versao_remota()
        if remota:
            (base / "versao.txt").write_text(remota, encoding="utf-8")

        shutil.rmtree(tmp, ignore_errors=True)
        return True

    def reiniciar(self) -> None:
        subprocess.Popen([sys.executable])
        os._exit(0)
