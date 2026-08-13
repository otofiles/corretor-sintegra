from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from core.engine import Engine
from core.models import MODO_AUTO_RELATAR, MODO_SOMENTE_RELATAR
from core.plugin_manager import PluginManager
from core.report import gerar_texto
from core.settings import Settings


class TesteEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = RAIZ
        cls.pasta_corretores = cls.raiz / "corretores"
        cls.pasta_data = cls.raiz / "data"
        cls.pasta_data.mkdir(exist_ok=True)
        cls.entrada = cls.raiz / "testes" / "fixtures" / "SINTEGRA_EXEMPLO_SINTETICO.TXT"
        cls.gestor = PluginManager(cls.pasta_corretores)
        cls.plugins = cls.gestor.scan()

    def setUp(self):
        self.destino = self.pasta_data / "teste_entrada.txt"
        shutil.copy2(self.entrada, self.destino)

    def tearDown(self):
        for sufixo in (".bak",):
            caminho = self.pasta_data / f"teste_entrada.txt{sufixo}"
            if caminho.exists():
                caminho.unlink()

    def test_plugins_carregados(self):
        self.assertTrue(self.plugins, self.gestor.avisos)
        ids = {p.id for p in self.plugins}
        self.assertIn("corretor_ie", ids)
        self.assertIn("corretor_cst061", ids)
        self.assertIn("corretor_cfop_transporte_registro50", ids)
        self.assertIn("corretor_cnpj", ids)
        self.assertIn("corretor_uf", ids)
        self.assertIn("corretor_cfop", ids)
        self.assertIn("corretor_data", ids)
        self.assertIn("corretor_modelo", ids)
        self.assertIn("corretor_numero", ids)
        self.assertIn("corretor_valores", ids)
        self.assertIn("corretor_registro90", ids)
        self.assertIn("corretor_cfop_item_registro50", ids)
        self.assertIn("corretor_registro51_modelo", ids)

    def test_cfop_transporte_aponta_modelo_incorreto(self):
        cfop = next(
            p for p in self.plugins
            if p.id == "corretor_cfop_transporte_registro50"
        )
        arquivo = self.pasta_data / "CFOP DE TRANSPORTE (com erro).txt"
        if not arquivo.exists():
            self.skipTest("arquivo de exemplo de CFOP de transporte ausente")
        settings = Settings(self.pasta_data / "settings.json")
        settings.carregar([cfop])
        settings.plugins[cfop.id] = {"habilitado": True, "modo": MODO_AUTO_RELATAR}
        resultado = Engine(settings, [cfop]).executar(arquivo)
        self.assertGreaterEqual(len(resultado.itens), 3)
        self.assertTrue(all(not i.corrigir for i in resultado.itens))
        self.assertTrue(all(i.confianca == "ALTA" for i in resultado.itens))
        self.assertTrue(all(i.tipo_registro == "50" for i in resultado.itens))
        self.assertIn("CT-e (modelo 57)", resultado.itens[0].descricao)
        self.assertIsNone(resultado.backup)

    def test_modo_somente_relatar_nao_altera_arquivo(self):
        settings = Settings(self.pasta_data / "settings.json")
        settings.carregar(self.plugins)
        for p in self.plugins:
            settings.plugins[p.id] = {"habilitado": True, "modo": MODO_SOMENTE_RELATAR}
        original = self.destino.read_bytes()
        resultado = Engine(settings, self.plugins).executar(self.destino)
        self.assertEqual(self.destino.read_bytes(), original)
        self.assertIsNone(resultado.backup)
        texto = gerar_texto(resultado, {p.id: p.nome for p in self.plugins})
        self.assertIn("RELATÓRIO DE ANÁLISE", texto)

    def test_modo_auto_corrigir_gera_backup(self):
        settings = Settings(self.pasta_data / "settings.json")
        settings.carregar(self.plugins)
        for p in self.plugins:
            settings.plugins[p.id] = {"habilitado": True, "modo": MODO_AUTO_RELATAR}
        original = self.destino.read_bytes()
        resultado = Engine(settings, self.plugins).executar(self.destino)
        if resultado.itens_aplicados:
            self.assertIsNotNone(resultado.backup)
            self.assertTrue(resultado.backup.exists())
            self.assertEqual(
                (self.pasta_data / "teste_entrada.txt.bak").read_bytes(),
                original,
            )
        else:
            self.assertIsNone(resultado.backup)


class TesteValidacao(unittest.TestCase):
    def test_validar_cnpj(self):
        from core.validacao import validar_cnpj

        self.assertTrue(validar_cnpj("11.222.333/0001-81" and "11222333000181"))
        self.assertFalse(validar_cnpj("11222333000182"))
        self.assertFalse(validar_cnpj("00000000000000"))

    def test_validar_cpf(self):
        from core.validacao import validar_cpf

        self.assertTrue(validar_cpf("52998224725"))
        self.assertFalse(validar_cpf("52998224726"))

    def test_eh_data_valida(self):
        from core.validacao import eh_data_valida

        self.assertTrue(eh_data_valida("20260701"))
        self.assertFalse(eh_data_valida("20260230"))
        self.assertFalse(eh_data_valida("abc"))

    def test_ultimo_dia_do_mes(self):
        from core.validacao import ultimo_dia_do_mes

        self.assertEqual(ultimo_dia_do_mes("20260201"), "20260228")
        self.assertEqual(ultimo_dia_do_mes("20260701"), "20260731")

    def test_validar_cfop(self):
        from core.validacao import validar_cfop

        self.assertTrue(validar_cfop("5102"))
        self.assertFalse(validar_cfop("0000"))
        self.assertFalse(validar_cfop("4102"))
        self.assertFalse(validar_cfop("123"))


class TesteNovosPlugins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = RAIZ
        cls.pasta_corretores = cls.raiz / "corretores"
        cls.pasta_data = cls.raiz / "data"
        cls.pasta_data.mkdir(exist_ok=True)
        cls.gestor = PluginManager(cls.pasta_corretores)
        cls.plugins = cls.gestor.scan()
        cls.entrada = cls.raiz / "testes" / "fixtures" / "SINTEGRA_EXEMPLO_SINTETICO.TXT"
        cls.original = cls.entrada.read_text(encoding="latin-1")

    def _rodar(self, plugin_id, conteudo=None, modo=MODO_AUTO_RELATAR):
        plugin = next(p for p in self.plugins if p.id == plugin_id)
        arquivo = self.pasta_data / f"teste_{plugin_id}.txt"
        texto = conteudo if conteudo is not None else self.original
        arquivo.write_text(texto, encoding="latin-1")
        settings = Settings(self.pasta_data / "settings.json")
        settings.carregar([plugin])
        settings.plugins[plugin.id] = {"habilitado": True, "modo": modo}
        resultado = Engine(settings, [plugin]).executar(arquivo)
        arquivo.unlink()
        return resultado

    def _linha_10(self, cnpj, uf="SP", data_inicial="20260701"):
        data_final = "20260731"
        return (
            "10" + cnpj.ljust(14) + " " * 14 + " " * 35 + " " * 30
            + uf + "0" * 10 + data_inicial + data_final + "1" + "2" + "5"
        )

    def _linha_50(self, modelo="55", numero="000001", cfop="5102",
                  serie="   ", aliquota="1700", valor="0000000000000",
                  situacao="N"):
        return (
            "50" + "0" * 14 + " " * 14 + "20260715" + "SP" + modelo
            + serie + numero + cfop + "P"
            + valor + "0" * 13 + "0" * 13 + "0" * 13 + "0" * 13
            + aliquota + situacao
        )

    def _linha_51(self, numero="000001", cfop="5102", serie="   "):
        return (
            "51" + "0" * 14 + " " * 14 + "20260715" + "SP"
            + serie + numero + cfop
        ).ljust(126)

    def test_corretor_cnpj_recalcula_dv(self):
        from core.validacao import dv_cnpj

        base = "112223330001"
        valido = base + dv_cnpj(base)
        errado = valido[:13] + ("0" if valido[13] != "0" else "1")
        linha = self._linha_10(errado)
        resultado = self._rodar("corretor_cnpj", "\n".join([linha]))
        self.assertEqual(len(resultado.itens), 1)
        item = resultado.itens[0]
        self.assertTrue(item.corrigir)
        self.assertIn(valido, item.texto_corrigido)

    def test_corretor_cnpj_aponta_cnpj_invalido(self):
        linha = self._linha_10("12X45678901234")
        resultado = self._rodar("corretor_cnpj", "\n".join([linha]))
        self.assertEqual(len(resultado.itens), 1)
        self.assertFalse(resultado.itens[0].corrigir)

    def test_corretor_uf_aponta_uf_invalida(self):
        linha = self._linha_10("00000000000000", uf="ZZ")
        resultado = self._rodar("corretor_uf", "\n".join([linha]))
        self.assertEqual(len(resultado.itens), 1)
        self.assertIn("ZZ", resultado.itens[0].descricao)

    def test_corretor_cfop_aponta_estrutura(self):
        linha = self._linha_50(cfop="4102")
        resultado = self._rodar("corretor_cfop", "\n".join([linha]))
        self.assertEqual(len(resultado.itens), 1)
        self.assertFalse(resultado.itens[0].corrigir)

    def test_corretor_data_aponta_data_invalida(self):
        linha = self._linha_10("00000000000000", data_inicial="20261301")
        resultado = self._rodar("corretor_data", "\n".join([linha]))
        self.assertGreaterEqual(len(resultado.itens), 1)
        self.assertIn("não é uma data", resultado.itens[0].descricao)

    def test_corretor_modelo_aponta_modelo_incorreto(self):
        linha = self._linha_50(modelo="99")
        resultado = self._rodar("corretor_modelo", "\n".join([linha]))
        self.assertEqual(len(resultado.itens), 1)
        self.assertIn("Modelo 99", resultado.itens[0].descricao)

    def test_corretor_numero_aponta_numero_zerado(self):
        linha = self._linha_50(numero="000000")
        resultado = self._rodar("corretor_numero", "\n".join([linha]))
        self.assertEqual(len(resultado.itens), 1)
        self.assertIn("zeros", resultado.itens[0].descricao)

    def test_corretor_valores_aponta_nao_numerico(self):
        linha = self._linha_50(valor="12AB000000000")
        resultado = self._rodar("corretor_valores", "\n".join([linha]))
        self.assertEqual(len(resultado.itens), 1)
        self.assertIn("não é um valor numérico", resultado.itens[0].descricao)

    def test_corretor_registro90_corrige_total(self):
        linhas = self.original.splitlines()
        ultima = linhas[-1]
        alterada = (
            ultima.replace("5000000008", "5000000009", 1)
            .replace("9900000092", "9900000093", 1)
        )
        linhas[-1] = alterada
        conteudo = "\n".join(linhas)
        resultado = self._rodar("corretor_registro90", conteudo)
        self.assertGreaterEqual(len(resultado.itens), 1)
        item = next(i for i in resultado.itens if i.corrigir)
        self.assertIn("5000000008", item.texto_corrigido)
        self.assertIn("9900000092", item.texto_corrigido)

    def _linha_54(self, numero="000001", cfop="5102"):
        linha = (
            "54" + "0" * 14 + " " * 5 + numero + cfop
            + "0" * (126 - (2 + 14 + 5 + 6 + 4))
        )
        return linha

    def test_corretor_cfop_item_aponta_divergente(self):
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            self._linha_50(numero="000001", cfop="1403"),
            self._linha_54(numero="000001", cfop="1102"),
        ])
        resultado = self._rodar("corretor_cfop_item_registro50", conteudo)
        self.assertEqual(len(resultado.itens), 1)
        item = resultado.itens[0]
        self.assertFalse(item.corrigir)
        self.assertEqual(item.confianca, "ALTA")
        self.assertEqual(item.tipo_registro, "54")
        self.assertIn("1403", item.descricao)

    def test_corretor_cfop_item_nao_aponta_quando_casa(self):
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            self._linha_50(numero="000001", cfop="1403"),
            self._linha_54(numero="000001", cfop="1403"),
        ])
        resultado = self._rodar("corretor_cfop_item_registro50", conteudo)
        self.assertEqual(len(resultado.itens), 0)

    def test_corretor_cfop_item_nao_aponta_multi_cfop_legitimo(self):
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            self._linha_50(numero="000001", cfop="1403"),
            self._linha_50(numero="000001", cfop="1102"),
            self._linha_54(numero="000001", cfop="1403"),
            self._linha_54(numero="000001", cfop="1102"),
        ])
        resultado = self._rodar("corretor_cfop_item_registro50", conteudo)
        self.assertEqual(len(resultado.itens), 0)

    def test_corretor_registro51_modelo_ok(self):
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            self._linha_50(numero="000001", modelo="01"),
            self._linha_51(numero="000001", cfop="5102"),
        ])
        resultado = self._rodar("corretor_registro51_modelo", conteudo)
        self.assertEqual(len(resultado.itens), 0)

    def test_corretor_registro51_modelo_aponta_diferente(self):
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            self._linha_50(numero="000001", modelo="55"),
            self._linha_51(numero="000001", cfop="5102"),
        ])
        resultado = self._rodar("corretor_registro51_modelo", conteudo)
        self.assertEqual(len(resultado.itens), 1)
        item = resultado.itens[0]
        self.assertFalse(item.corrigir)
        self.assertEqual(item.confianca, "ALTA")
        self.assertEqual(item.tipo_registro, "51")
        self.assertIn("55", item.descricao)
        self.assertIn("01", item.descricao)

    def test_corretor_registro51_modelo_aponta_cfop_divergente(self):
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            self._linha_50(numero="000001", modelo="01", cfop="5102"),
            self._linha_51(numero="000001", cfop="1102"),
        ])
        resultado = self._rodar("corretor_registro51_modelo", conteudo)
        self.assertEqual(len(resultado.itens), 1)
        self.assertIn("000001", resultado.itens[0].descricao)

    def test_corretor_registro51_modelo_aponta_sem_reg50(self):
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            self._linha_51(numero="000001", cfop="5102"),
        ])
        resultado = self._rodar("corretor_registro51_modelo", conteudo)
        self.assertEqual(len(resultado.itens), 1)

    def test_corretor_registro51_modelo_nao_aponta_multi_modelo(self):
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            self._linha_50(numero="000001", modelo="01"),
            self._linha_50(numero="000001", modelo="55"),
            self._linha_51(numero="000001", cfop="5102"),
        ])
        resultado = self._rodar("corretor_registro51_modelo", conteudo)
        self.assertEqual(len(resultado.itens), 0)

    def test_corretor_registro51_modelo_nao_aponta_reg50_outro_cnpj(self):
        linha_50_outro = (
            "50" + "9" * 14 + " " * 14 + "20260715" + "SP"
            + "01" + "   " + "000001" + "5102"
        ).ljust(126)
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            linha_50_outro,
            self._linha_51(numero="000001", cfop="5102"),
        ])
        resultado = self._rodar("corretor_registro51_modelo", conteudo)
        self.assertEqual(len(resultado.itens), 0)

    def test_corretor_cfop_item_aponta_sem_reg50(self):
        conteudo = "\n".join([
            self._linha_10("00000000000000"),
            self._linha_54(numero="000002", cfop="1102"),
        ])
        resultado = self._rodar("corretor_cfop_item_registro50", conteudo)
        self.assertEqual(len(resultado.itens), 1)
        self.assertFalse(resultado.itens[0].corrigir)
        self.assertIn("000002", resultado.itens[0].descricao)

    def test_arquivo_exemplo_nao_gera_falsos_positivos_novos(self):
        ids_novos = {
            "corretor_cnpj", "corretor_uf", "corretor_cfop", "corretor_data",
            "corretor_modelo", "corretor_numero",
            "corretor_valores", "corretor_registro90",
        }
        plugin = next(
            p for p in self.plugins
            if p.id == "corretor_cfop_transporte_registro50"
        )
        settings = Settings(self.pasta_data / "settings.json")
        settings.carregar(self.plugins)
        for p in self.plugins:
            settings.plugins[p.id] = {"habilitado": True, "modo": MODO_SOMENTE_RELATAR}
        arquivo = self.pasta_data / "teste_falsos_positivos.txt"
        arquivo.write_text(self.original, encoding="latin-1")
        resultado = Engine(settings, self.plugins).executar(arquivo)
        arquivo.unlink()
        for item in resultado.itens:
            self.assertNotIn(item.plugin, ids_novos)


if __name__ == "__main__":
    unittest.main()
