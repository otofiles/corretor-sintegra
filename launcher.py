from __future__ import annotations

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
import importlib.util
import sys
import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.scrolledtext
from tkinter import Tk, Label, messagebox
from urllib.request import Request, urlopen


def instalar_log_erros(base: Path) -> None:
    if not getattr(sys, "frozen", False):
        return
    try:
        base.mkdir(parents=True, exist_ok=True)
        log = base / "erro.log"
        sys.stderr = open(log, "a", encoding="utf-8", errors="replace")
        sys.stdout = sys.stderr
    except Exception:
        pass


REPOSITORIO = "otofiles/corretor-sintegra"
NOME_ASSET = "corretor_sintegra.zip"
PASTA_APP = "CorretorSINTEGRA"
TEMPO_LIMITE = 30
AGENTE = {"User-Agent": "CorretorSINTEGRA"}


def _api_url() -> str:
    override = os.environ.get("CORRETOR_API_URL")
    if override:
        return override
    return f"https://api.github.com/repos/{REPOSITORIO}/releases/latest"


def _baixar(url: str) -> bytes:
    req = Request(url, headers=AGENTE)
    with urlopen(req, timeout=TEMPO_LIMITE) as resp:
        return resp.read()


def _comparar(a: str, b: str) -> int:
    pa = [int(x) for x in a.split(".") if x.isdigit()]
    pb = [int(x) for x in b.split(".") if x.isdigit()]
    for x, y in zip(pa, pb):
        if x != y:
            return 1 if x > y else -1
    return (len(pa) > len(pb)) - (len(pa) < len(pb))


def pasta_base() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / PASTA_APP
    return Path.home() / PASTA_APP


def caminho_icone() -> Path | None:
    if getattr(sys, "frozen", False):
        candidato = Path(sys._MEIPASS) / "art" / "ico2.ico"
        if candidato.exists():
            return candidato
    candidato = Path(__file__).resolve().parent / "corretor_sintegra" / "art" / "ico2.ico"
    return candidato if candidato.exists() else None


def versao_local_arquivo(base: Path) -> str:
    arquivo = base / "versao.txt"
    if arquivo.exists():
        return arquivo.read_text(encoding="utf-8").strip() or "0.0.0"
    return "0.0.0"


def versao_remota() -> str | None:
    try:
        dados = json.loads(_baixar(_api_url()).decode("utf-8"))
    except Exception:
        return None
    tag = dados.get("tag_name", "")
    return tag.lstrip("vV") or None


def url_asset() -> str | None:
    override = os.environ.get("CORRETOR_ASSET_URL")
    if override:
        return override
    try:
        dados = json.loads(_baixar(_api_url()).decode("utf-8"))
    except Exception:
        return None
    for asset in dados.get("assets", []):
        if asset.get("name") == NOME_ASSET:
            return asset.get("browser_download_url")
    return None


def _splash(icone: Path | None) -> Tk:
    root = Tk()
    root.title("Corretor SINTEGRA")
    root.geometry("380x130")
    root.resizable(False, False)
    if icone:
        try:
            root.iconbitmap(str(icone))
        except Exception:
            pass
    Label(
        root,
        text="Corretor SINTEGRA",
        font=("Segoe UI", 16, "bold"),
        fg="#12315b",
        pady=8,
    ).pack()
    status = Label(
        root,
        text="Inicializando...",
        font=("Segoe UI", 10),
        fg="#5f6368",
    )
    status.pack(pady=(4, 0))
    root.update()
    return root, status


def _atualizar_status(status, texto: str) -> None:
    try:
        status.config(text=texto)
        status.update()
    except Exception:
        pass


def baixar_e_extrair(base: Path, pacote: Path, versao: str, status) -> None:
    url = url_asset()
    if not url:
        raise RuntimeError("Pacote de atualização não encontrado no GitHub.")
    _atualizar_status(status, f"Baixando atualização {versao}...")
    conteudo = _baixar(url)

    tmp = base / "_tmp_atualizacao"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    zip_path = tmp / NOME_ASSET
    zip_path.write_bytes(conteudo)

    _atualizar_status(status, "Extraindo atualização...")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(tmp)

    novo = tmp / "corretor_sintegra"
    if not novo.exists():
        raise RuntimeError("Pacote de atualização com formato inválido.")

    if pacote.exists():
        shutil.rmtree(pacote)
    shutil.move(str(novo), str(pacote))
    (base / "versao.txt").write_text(versao or "", encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)


def principal() -> int:
    base = pasta_base()
    instalar_log_erros(base)
    icone = caminho_icone()
    root, status = _splash(icone)

    base = pasta_base()
    base.mkdir(parents=True, exist_ok=True)
    pacote = base / "corretor_sintegra"
    local_ver = versao_local_arquivo(base)

    try:
        remota = versao_remota()
    except Exception:
        remota = None

    if remota and (not pacote.exists() or _comparar(remota, local_ver) > 0):
        try:
            baixar_e_extrair(base, pacote, remota, status)
        except Exception as exc:
            if not pacote.exists():
                root.destroy()
                messagebox.showerror(
                    "Erro de atualização",
                    f"Não foi possível baixar o aplicativo: {exc}",
                )
                return 1
            _atualizar_status(status, "Usando versão em cache.")

    elif remota is None and not pacote.exists():
        root.destroy()
        messagebox.showerror(
            "Sem conexão",
            "Não foi possível verificar atualizações e o aplicativo não está "
            "instalado localmente. Conecte-se à internet e tente novamente.",
        )
        return 1

    root.destroy()

    sys.path.insert(0, str(pacote))
    import main as app_main

    return app_main.main(pacote)


if __name__ == "__main__":
    sys.exit(principal())
