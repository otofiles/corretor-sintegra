from __future__ import annotations

from typing import List, Optional, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro
from core.validacao import UFS

CAMPOS_UF = {
    "10": (95, 97),
    "50": (38, 40),
    "53": (38, 40),
    "55": (38, 40),
    "70": (38, 40),
    "71": (38, 40),
    "74": (79, 81),
    "76": (59, 61),
    "86": (50, 52),
}

_DESCRICAO_CAMPO = {
    "10": "UF do informante",
    "50": "UF",
    "53": "UF",
    "55": "UF",
    "70": "UF",
    "71": "UF",
    "74": "UF",
    "76": "UF",
    "86": "UF",
}


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    pos = CAMPOS_UF.get(registro.tipo)
    if not pos:
        return []
    inicio, fim = pos
    linha = registro.conteudo
    if len(linha) < fim:
        return []
    uf = linha[inicio:fim].strip()
    if not uf:
        return []
    if uf.upper() in UFS:
        return []
    itens = [
        ItemCorrecao(
            numero_linha=registro.numero_linha,
            tipo_registro=registro.tipo,
            texto_original=linha,
            confianca="ALTA",
            descricao=(
                f"{_DESCRICAO_CAMPO[registro.tipo]}: UF {uf!r} não é uma "
                f"sigla de unidade federativa válida (use uma das 27 UFs ou "
                f"'EX' para exterior)."
            ),
            regra="UF inválida",
            corrigir=False,
        )
    ]
    return itens


plugin = CorretorPlugin(
    id="corretor_uf",
    nome="Corretor de UF",
    descricao="Identifica siglas de UF inexistentes nos registros 10, 50, 53, 55, 70, 71, 74, 76 e 86.",
    versao="1.0",
    registros_afetados=["10", "50", "53", "55", "70", "71", "74", "76", "86"],
    analisar=_analisar,
)
