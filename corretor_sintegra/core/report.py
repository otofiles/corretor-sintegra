from __future__ import annotations

import csv
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .models import ItemCorrecao, ResultadoExecucao


def gerar_texto(resultado: ResultadoExecucao, nomes: Dict[str, str]) -> str:
    linhas = []
    linhas.append("=" * 72)
    linhas.append("RELATÓRIO DE ANÁLISE E CORREÇÃO — SINTEGRA")
    linhas.append("=" * 72)
    linhas.append(f"Arquivo        : {resultado.caminho}")
    linhas.append(f"Data/hora      : {datetime.now():%d/%m/%Y %H:%M:%S}")
    linhas.append(f"Backup criado  : {resultado.backup if resultado.backup else 'não'}")
    linhas.append(f"Total registros: {resultado.total_registros}")
    linhas.append(f"Corretores ativos: {resultado.total_plugins}")
    linhas.append("")
    linhas.append("Resumo por corretor:")
    linhas.append("-" * 72)
    linhas.append(f"{'Corretor':<34}{'Total':>7}{'Corrigidos':>11}{'Apontados':>11}{'Erros':>7}")
    for p_id, stats in resultado.por_plugin.items():
        nome = nomes.get(p_id, p_id)
        linhas.append(
            f"{nome:<34}{stats.total:>7}{stats.corrigidos:>11}"
            f"{stats.apontados:>11}{stats.erros:>7}"
        )
    linhas.append("")
    linhas.append("-" * 72)
    linhas.append("DETALHES")
    linhas.append("-" * 72)
    if not resultado.itens:
        linhas.append("Nenhum item encontrado para revisão.")
    aplicados = {id(i) for i in resultado.itens_aplicados}
    for item in resultado.itens:
        status = "CORRIGIDO" if id(item) in aplicados else "APONTAMENTO"
        linhas.append(
            f"[{status}] Linha {item.numero_linha} | Tipo {item.tipo_registro} "
            f"| Confiança {item.confianca}"
        )
        linhas.append(f"    Corretor : {nomes.get(item.plugin, item.plugin)}")
        linhas.append(f"    Regra    : {item.regra or '-'}")
        linhas.append(f"    Descrição: {item.descricao or '-'}")
        linhas.append(f"    Original : {item.texto_original}")
        if item.texto_corrigido is not None:
            linhas.append(f"    Corrigido: {item.texto_corrigido}")
        linhas.append("")
    return "\n".join(linhas)


def gerar_csv(resultado: ResultadoExecucao, nomes: Dict[str, str]) -> str:
    saida = io.StringIO()
    writer = csv.writer(saida, delimiter=";")
    writer.writerow(
        ["linha", "tipo", "status", "corretor", "confianca", "regra", "descricao", "original", "corrigido"]
    )
    aplicados = {id(i) for i in resultado.itens_aplicados}
    for item in resultado.itens:
        status = "CORRIGIDO" if id(item) in aplicados else "APONTAMENTO"
        writer.writerow(
            [
                item.numero_linha,
                item.tipo_registro,
                status,
                nomes.get(item.plugin, item.plugin),
                item.confianca,
                item.regra,
                item.descricao,
                item.texto_original,
                item.texto_corrigido if item.texto_corrigido is not None else "",
            ]
        )
    return saida.getvalue()


def salvar_relatorio_txt(pasta: Path, texto: str) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"relatorio_{datetime.now():%Y%m%d_%H%M%S}.txt"
    caminho.write_text(texto, encoding="utf-8")
    return caminho


GUIA_AMIGAVEL = {
    "corretor_ie": "confira o número da Inscrição Estadual (IE) informado",
    "corretor_cnpj": "confira o CNPJ/CPF informado",
    "corretor_aliquota": "confira a alíquota informada (máximo 25%)",
    "corretor_cfop": "confira o CFOP informado (4 dígitos)",
    "corretor_cfop_transporte_registro50": (
        "confira o CFOP de transporte (deve usar modelo CT-e 57/67)"
    ),
    "corretor_cst061": "confira se o CST 061 é o correto para a operação",
    "corretor_data": "confira a data informada (formato DDMMAA)",
    "corretor_modelo": "confira o modelo do documento informado",
    "corretor_numero": "confira o número do documento informado",
    "corretor_registro90": "confira os totais declarados no registro 90",
    "corretor_uf": "confira a sigla da UF informada",
    "corretor_valores": "confira o valor informado",
}

GUIA_GENERICO = "confira os dados deste registro no sistema"


def _extrair_numero_nota(item: ItemCorrecao) -> Optional[str]:
    import re

    padroes = (
        r"Nota fiscal\s+(\d+)",
        r"Número\s+(\d+)",
        r"nota\s+(\d+)",
        r"nº\s+(\d+)",
    )
    for padrao in padroes:
        m = re.search(padrao, item.descricao or "")
        if m:
            return m.group(1)
    return None


def gerar_relatorio_amigavel(resultado: ResultadoExecucao, nomes: Dict[str, str]) -> str:
    aplicados_ids = {id(i) for i in resultado.itens_aplicados}
    apontados = [i for i in resultado.itens if id(i) not in aplicados_ids]

    if not apontados:
        return (
            "ANÁLISE CONCLUÍDA\n"
            "=================\n"
            "\n"
            "Tudo certo com o seu arquivo, basta validar ele novamente dentro do Validador do Sintegra"
        )

    linhas = ["ANÁLISE CONCLUÍDA", "=================", ""]
    linhas.append("O arquivo precisa de ajustes:")
    linhas.append("")
    for item in apontados:
        nota = _extrair_numero_nota(item)
        guia = GUIA_AMIGAVEL.get(item.plugin, GUIA_GENERICO)
        alvo = f"Nota {nota}" if nota else f"Linha {item.numero_linha}"
        linhas.append(f"- {alvo}: {guia}")
    linhas.append("")
    linhas.append("Depois de corrigir, valide novamente o arquivo.")
    return "\n".join(linhas)


def salvar_log_tecnico(pasta_logs: Path, texto: str) -> Path:
    pasta_logs.mkdir(parents=True, exist_ok=True)
    caminho = pasta_logs / f"log_{datetime.now():%Y%m%d_%H%M%S}.txt"
    caminho.write_text(texto, encoding="utf-8")
    return caminho
