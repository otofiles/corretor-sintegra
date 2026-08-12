from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro
from core.validacao import eh_data_valida, ultimo_dia_do_mes

CAMPOS_DATA = {
    "50": [(30, 38, "data de emissão/recebimento")],
    "53": [(30, 38, "data de emissão/recebimento")],
    "61": [(30, 38, "data de emissão")],
    "70": [(30, 38, "data de emissão")],
    "71": [(30, 38, "data de emissão")],
    "74": [(2, 10, "data do inventário")],
    "75": [
        (2, 10, "data inicial de validade"),
        (10, 18, "data final de validade"),
    ],
    "76": [(51, 59, "data de emissão")],
    "85": [
        (13, 21, "data da declaração de exportação"),
        (34, 42, "data do RE"),
        (58, 66, "data do conhecimento"),
        (80, 88, "data da averbação"),
        (94, 102, "data de emissão da NF"),
    ],
    "86": [(14, 22, "data do RE"), (58, 66, "data de emissão da NF")],
}

_ESTADO: Dict[str, Optional[str]] = {"data_inicial": None, "data_final": None}


def _reiniciar_periodo() -> None:
    _ESTADO["data_inicial"] = None
    _ESTADO["data_final"] = None


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    linha = registro.conteudo
    itens: List[ItemCorrecao] = []

    if registro.tipo == "10":
        _reiniciar_periodo()
        if len(linha) < 123:
            return []
        inicial = linha[107:115]
        final = linha[115:123]
        if eh_data_valida(inicial) and eh_data_valida(final):
            _ESTADO["data_inicial"] = inicial
            _ESTADO["data_final"] = final
        if not eh_data_valida(inicial):
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro="10",
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"Data inicial do período: {inicial!r} não é uma data "
                        f"válida (esperado AAAAMMDD)."
                    ),
                    regra="Data inicial inválida no registro 10",
                    corrigir=False,
                )
            )
        if not eh_data_valida(final):
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro="10",
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"Data final do período: {final!r} não é uma data "
                        f"válida (esperado AAAAMMDD)."
                    ),
                    regra="Data final inválida no registro 10",
                    corrigir=False,
                )
            )
        if eh_data_valida(inicial) and inicial[6:8] != "01":
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro="10",
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"Data inicial do período {inicial} deve ser o dia 01 "
                        f"do mês."
                    ),
                    regra="Data inicial deve ser dia 01",
                    corrigir=False,
                )
            )
        if eh_data_valida(inicial) and eh_data_valida(final):
            ultimo = ultimo_dia_do_mes(inicial)
            if final != ultimo:
                itens.append(
                    ItemCorrecao(
                        numero_linha=registro.numero_linha,
                        tipo_registro="10",
                        texto_original=linha,
                        confianca="ALTA",
                        descricao=(
                            f"Data final do período {final} não corresponde ao "
                            f"último dia do mês da data inicial ({ultimo})."
                        ),
                        regra="Data final deve ser o último dia do mês",
                        corrigir=False,
                    )
                )
        return itens

    campos = CAMPOS_DATA.get(registro.tipo)
    if not campos:
        return []
    if registro.tipo == "61" and len(linha) > 2 and linha[2] == "R":
        return []

    for inicio, fim, nome in campos:
        if len(linha) < fim:
            continue
        valor = linha[inicio:fim].strip()
        if not valor:
            continue
        if not eh_data_valida(valor):
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro=registro.tipo,
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"{nome}: {valor!r} não é uma data válida "
                        f"(esperado AAAAMMDD)."
                    ),
                    regra="Data inválida",
                    corrigir=False,
                )
            )
            continue
        if registro.tipo == "75":
            continue
        if _ESTADO["data_inicial"] and _ESTADO["data_final"]:
            if valor < _ESTADO["data_inicial"] or valor > _ESTADO["data_final"]:
                itens.append(
                    ItemCorrecao(
                        numero_linha=registro.numero_linha,
                        tipo_registro=registro.tipo,
                        texto_original=linha,
                        confianca="MEDIA",
                        descricao=(
                            f"{nome}: {valor} fora do período informado no "
                            f"registro 10 "
                            f"({_ESTADO['data_inicial']} a "
                            f"{_ESTADO['data_final']})."
                        ),
                        regra="Data fora do período do registro 10",
                        corrigir=False,
                    )
                )

    return itens


plugin = CorretorPlugin(
    id="corretor_data",
    nome="Corretor de Datas",
    descricao=(
        "Valida datas (AAAAMMDD) em vários registros. No registro 10, verifica "
        "se a data inicial é dia 01 e a final é o último dia do mês; nos "
        "documentos, aponta datas fora do período declarado."
    ),
    versao="1.0",
    registros_afetados=[
        "10", "50", "53", "61", "70", "71", "74", "75", "76", "85", "86",
    ],
    analisar=_analisar,
)
