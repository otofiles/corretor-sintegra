from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from textwrap import dedent

RAIZ = Path(__file__).resolve().parent.parent
VERSAO_PY = RAIZ / "corretor_sintegra" / "core" / "versao.py"


def ler_versao() -> str:
    texto = VERSAO_PY.read_text(encoding="utf-8")
    for linha in texto.splitlines():
        if linha.strip().startswith("VERSAO"):
            return linha.split("=", 1)[1].strip().strip('"').strip("'")
    return "1.0.0"


def gerar_version_info(versao: str) -> Path:
    maior, menor, patch = (versao.split(".") + ["0", "0", "0"])[:3]
    numeros = (int(maior), int(menor), int(patch), 0)
    caminho = Path(__file__).resolve().parent / "_version_info.txt"
    conteudo = dedent(
        f'''
        VSVersionInfo(
            ffi=FixedFileInfo(
                filevers={numeros},
                prodvers={numeros},
                mask=0x3F,
                flags=0x0,
                OS=0x40004,
                fileType=0x1,
                subtype=0x0,
                date=(0, 0),
            ),
            kids=[
                StringFileInfo([
                    StringTable(
                        u"040904B0",
                        [StringStruct(u"CompanyName", u"otofiles"),
                         StringStruct(u"FileDescription", u"Corretor SINTEGRA"),
                         StringStruct(u"FileVersion", u"{versao}"),
                         StringStruct(u"InternalName", u"CorretorSINTEGRA"),
                         StringStruct(u"LegalCopyright", u"Copyright (c) otofiles"),
                         StringStruct(u"OriginalFilename", u"CorretorSINTEGRA.exe"),
                         StringStruct(u"ProductName", u"Corretor SINTEGRA"),
                         StringStruct(u"ProductVersion", u"{versao}")]),
                ]),
                VarFileInfo([VarStruct(u"Translation", [1033, 1200])]),
            ],
        )
        '''
    )
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def main() -> int:
    versao = ler_versao()
    print(f"Versão detectada: {versao}")
    version_info = gerar_version_info(versao)

    comando = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--name=CorretorSINTEGRA",
        f"--icon={RAIZ / 'corretor_sintegra' / 'art' / 'ico2.ico'}",
        f"--add-data={RAIZ / 'corretor_sintegra' / 'art' / 'ico2.ico'};art",
        f"--version-file={version_info}",
        str(RAIZ / "launcher.py"),
    ]
    print("Executando PyInstaller...")
    resultado = subprocess.run(comando, cwd=RAIZ)
    if resultado.returncode != 0:
        print("Falha ao compilar o executável.")
        return resultado.returncode

    exe = RAIZ / "dist" / "CorretorSINTEGRA.exe"
    print(f"Executável gerado: {exe}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
