from __future__ import annotations

import re
from typing import List

from core.models import CorretorPlugin, ItemCorrecao, Registro

_PADRAO = re.compile(r"^54\s*\d{14}\s*\d{2}\s*\d\s*(\d{6})\s*\d{4}061\d{3}", re.MULTILINE)


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    match = _PADRAO.match(registro.conteudo)
    if not match:
        return []
    numero_nota = match.group(1)
    return [
        ItemCorrecao(
            numero_linha=registro.numero_linha,
            tipo_registro=registro.tipo,
            texto_original=registro.conteudo,
            confianca="ALTA",
            descricao=(
                f"Nota fiscal {numero_nota} com CST 061 identificada. "
                "Revise o enquadramento da operação."
            ),
            regra="CST 061",
            corrigir=False,
        )
    ]


plugin = CorretorPlugin(
    id="corretor_cst061",
    nome="Identificador de CST 061",
    descricao="Identifica notas fiscais com CST 061 nos registros 54 para revisão manual.",
    versao="1.0",
    registros_afetados=["54"],
    analisar=_analisar,
)
