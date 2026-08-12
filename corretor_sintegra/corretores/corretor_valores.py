from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro

CAMPOS_VALORES: Dict[str, List[Tuple[int, int, str]]] = {
    "50": [
        (56, 69, "valor total"),
        (69, 82, "base de cálculo ICMS"),
        (82, 95, "valor do ICMS"),
        (95, 108, "isenta/não tributada"),
        (108, 121, "outras"),
    ],
    "53": [
        (56, 69, "base de cálculo ICMS-ST"),
        (69, 82, "valor do ICMS retido"),
        (82, 95, "despesas acessórias"),
    ],
    "54": [
        (62, 74, "valor do produto"),
        (74, 86, "desconto/despesas"),
        (86, 98, "base de cálculo ICMS"),
        (98, 110, "base de cálculo ICMS-ST"),
        (110, 122, "valor do IPI"),
    ],
    "61": [
        (57, 70, "valor total"),
        (70, 83, "base de cálculo ICMS"),
        (83, 95, "valor do ICMS"),
        (95, 108, "isenta/não tributada"),
        (108, 121, "outras"),
    ],
    "70": [
        (55, 68, "valor total"),
        (68, 82, "base de cálculo ICMS"),
        (82, 96, "valor do ICMS"),
        (96, 110, "isenta/não tributada"),
        (110, 124, "outras"),
    ],
    "71": [
        (100, 114, "valor total da NF"),
    ],
    "74": [
        (24, 37, "quantidade"),
        (37, 50, "valor"),
    ],
    "76": [
        (61, 74, "valor total"),
        (74, 87, "base de cálculo ICMS"),
        (87, 99, "valor do ICMS"),
        (99, 111, "isenta/não tributada"),
        (111, 123, "outras"),
    ],
    "77": [
        (64, 76, "valor"),
        (76, 88, "desconto/despesas"),
        (88, 100, "base de cálculo ICMS"),
    ],
}


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    campos = CAMPOS_VALORES.get(registro.tipo)
    if not campos:
        return []
    linha = registro.conteudo
    if registro.tipo == "61" and len(linha) > 2 and linha[2] == "R":
        return []

    itens: List[ItemCorrecao] = []
    for inicio, fim, nome in campos:
        if len(linha) < fim:
            continue
        valor = linha[inicio:fim].strip()
        if not valor:
            continue
        if not valor.isdigit():
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro=registro.tipo,
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"{nome}: {valor!r} não é um valor numérico válido "
                        f"(campos de valor no SINTEGRA são numéricos, sem "
                        f"sinal nem separador)."
                    ),
                    regra="Valor com conteúdo inválido",
                    corrigir=False,
                )
            )

    return itens


plugin = CorretorPlugin(
    id="corretor_valores",
    nome="Corretor de Valores (formato)",
    descricao="Verifica se os campos de valor dos registros 50, 53, 54, 61, 70, 71, 74, 76 e 77 são numéricos (sem letras ou sinais).",
    versao="1.0",
    registros_afetados=["50", "53", "54", "61", "70", "71", "74", "76", "77"],
    analisar=_analisar,
)
