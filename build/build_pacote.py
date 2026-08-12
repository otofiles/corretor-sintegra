from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PACOTE = RAIZ / "corretor_sintegra"
DESTINO = RAIZ / "dist" / "corretor_sintegra.zip"

EXCLUIR_PARTES = {"__pycache__", ".git"}
EXCLUIR_RAIZ = {
    "testes",
    "aprendizado",
    "ui_backup_20260812",
}
EXCLUIR_ARQUIVOS = {"contexto.md", "requirements.txt"}
EXTENSOES_IGNORAR = {".pyc", ".bak"}


def deve_incluir(rel: Path) -> bool:
    partes = rel.parts
    if partes and partes[0] in EXCLUIR_RAIZ:
        return False
    for parte in partes:
        if parte in EXCLUIR_PARTES:
            return False
    if rel.name in EXCLUIR_ARQUIVOS:
        return False
    if rel.name.endswith(".pyc") or rel.suffix in EXTENSOES_IGNORAR:
        return False
    if rel.parts[:2] == ("data", "logs"):
        return False
    return True


def varrer() -> list[Path]:
    arquivos: list[Path] = []
    for caminho in PACOTE.rglob("*"):
        if not caminho.is_file():
            continue
        rel = caminho.relative_to(PACOTE)
        if deve_incluir(rel):
            arquivos.append(caminho)
    return sorted(arquivos)


def main() -> int:
    if not PACOTE.exists():
        print(f"Pacote não encontrado: {PACOTE}")
        return 1

    arquivos = varrer()
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as zf:
        for caminho in arquivos:
            rel = caminho.relative_to(PACOTE)
            zf.write(caminho, Path("corretor_sintegra") / rel)

    conteudo = DESTINO.read_bytes()
    sha = hashlib.sha256(conteudo).hexdigest()
    print(f"Pacote gerado: {DESTINO}")
    print(f"Arquivos: {len(arquivos)}")
    print(f"Tamanho: {len(conteudo)} bytes")
    print(f"SHA256: {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
