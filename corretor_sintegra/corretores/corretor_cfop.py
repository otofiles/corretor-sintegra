from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro
from core.validacao import validar_cfop

CAMPOS_CFOP = {
    "50": (51, 55),
    "53": (51, 55),
    "54": (27, 31),
    "70": (51, 55),
    "76": (46, 50),
    "77": (32, 36),
}

CAMPOS_SITUACAO = {
    "50": 125,
    "53": 95,
    "70": 125,
}

_DESCRICAO_CAMPO = {
    "50": "CFOP",
    "53": "CFOP",
    "54": "CFOP",
    "70": "CFOP",
    "76": "CFOP",
    "77": "CFOP",
}


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    pos = CAMPOS_CFOP.get(registro.tipo)
    if not pos:
        return []
    inicio, fim = pos
    linha = registro.conteudo
    if len(linha) < fim:
        return []
    cfop = linha[inicio:fim].strip()
    if not cfop:
        return []
    pos_situacao = CAMPOS_SITUACAO.get(registro.tipo)
    if (
        cfop == "0000"
        and pos_situacao is not None
        and len(linha) > pos_situacao
        and linha[pos_situacao] == "4"
    ):
        return []
    if validar_cfop(cfop):
        return []
    itens = [
        ItemCorrecao(
            numero_linha=registro.numero_linha,
            tipo_registro=registro.tipo,
            texto_original=linha,
            confianca="ALTA",
            descricao=(
                f"{_DESCRICAO_CAMPO[registro.tipo]}: CFOP {cfop!r} é "
                f"estruturalmente inválido (deve ter 4 dígitos, começar por "
                f"1, 2, 3, 5, 6 ou 7 e ser diferente de 0000)."
            ),
            regra="CFOP inválido",
            corrigir=False,
        )
    ]
    return itens


plugin = CorretorPlugin(
    id="corretor_cfop",
    nome="Corretor de CFOP (estrutural)",
    descricao="Identifica CFOPs estruturalmente inválidos (tamanho, primeiro dígito ou 0000) nos registros 50, 53, 54, 70, 76 e 77.",
    versao="1.0",
    registros_afetados=["50", "53", "54", "70", "76", "77"],
    analisar=_analisar,
)
