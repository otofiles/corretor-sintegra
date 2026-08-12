from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest import TestCase, mock

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "corretor_sintegra"))

from core import atualizador  # noqa: E402

PACOTE_ZIP = RAIZ / "dist" / "corretor_sintegra.zip"

import launcher  # noqa: E402


class TestAtualizador(TestCase):
    def test_comparar_versoes(self):
        self.assertEqual(atualizador._comparar_versoes("1.0.0", "1.0.0"), 0)
        self.assertEqual(atualizador._comparar_versoes("1.1.0", "1.0.9"), 1)
        self.assertEqual(atualizador._comparar_versoes("0.9.0", "1.0.0"), -1)

    def test_baixar_e_aplicar(self):
        if not PACOTE_ZIP.exists():
            self.skipTest("pacote em dist/ não foi construído")
        api = {
            "tag_name": "v2.3.4",
            "assets": [
                {
                    "name": "corretor_sintegra.zip",
                    "browser_download_url": "http://example.com/corretor_sintegra.zip",
                }
            ],
        }
        conteudo = PACOTE_ZIP.read_bytes()

        def fake_baixar(url):
            if "releases/latest" in url:
                return json.dumps(api).encode("utf-8")
            return conteudo

        base = Path(tempfile.mkdtemp())
        pacote = base / "corretor_sintegra"
        with mock.patch.object(atualizador, "_baixar", side_effect=fake_baixar), \
                mock.patch.object(atualizador.caminhos, "pasta_base", return_value=base), \
                mock.patch.object(atualizador.caminhos, "pasta_pacote", return_value=pacote):
            aut = atualizador.Atualizador()
            ok = aut.baixar_e_aplicar()
            self.assertTrue(ok)
            self.assertTrue((pacote / "main.py").exists())
            self.assertTrue((pacote / "core" / "atualizador.py").exists())
            self.assertEqual(
                (base / "versao.txt").read_text(encoding="utf-8"), "2.3.4"
            )


class TestLauncher(TestCase):
    def test_comparar(self):
        self.assertEqual(launcher._comparar("1.0.0", "1.0.0"), 0)
        self.assertEqual(launcher._comparar("2.0.0", "1.9.9"), 1)

    def test_versao_local_arquivo(self):
        base = Path(tempfile.mkdtemp())
        self.assertEqual(launcher.versao_local_arquivo(base), "0.0.0")
        (base / "versao.txt").write_text("3.2.1", encoding="utf-8")
        self.assertEqual(launcher.versao_local_arquivo(base), "3.2.1")

    def test_baixar_e_extrair(self):
        if not PACOTE_ZIP.exists():
            self.skipTest("pacote em dist/ não foi construído")
        base = Path(tempfile.mkdtemp())
        pacote = base / "corretor_sintegra"
        antigo = "file:///" + str(PACOTE_ZIP).replace("\\", "/")

        class StatusFake:
            def config(self, **_):
                pass

            def update(self):
                pass

        with mock.patch.dict("os.environ", {"CORRETOR_ASSET_URL": antigo}):
            launcher.baixar_e_extrair(base, pacote, "9.9.9", StatusFake())
        self.assertTrue((pacote / "main.py").exists())
        self.assertEqual(
            (base / "versao.txt").read_text(encoding="utf-8"), "9.9.9"
        )

    def test_build_zip_structure(self):
        if not PACOTE_ZIP.exists():
            self.skipTest("pacote em dist/ não foi construído")
        with zipfile.ZipFile(PACOTE_ZIP) as zf:
            nomes = zf.namelist()
        self.assertTrue(any(n.startswith("corretor_sintegra/main.py") for n in nomes))
        self.assertFalse(any("__pycache__" in n for n in nomes))
        self.assertFalse(any(n.startswith("corretor_sintegra/testes") for n in nomes))
        self.assertFalse(any(n.startswith("corretor_sintegra/ui_backup") for n in nomes))


if __name__ == "__main__":
    from unittest import main

    main()
