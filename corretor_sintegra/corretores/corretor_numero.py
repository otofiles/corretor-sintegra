from __future__ import annotations

from typing import List, Optional, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro

CAMPOS_NUMERO = {
    "50": (45, 51, "número da NF"),
    "53": (45, 51, "número da NF"),
    "54": (21, 27, "número da NF"),
    "61": [(45, 51, "número inicial"), (51, 57, "número final")],
    "70": (45, 51, "número do documento"),
    "71": (45, 51, "número do documento"),
    "76": (36, 46, "número do documento"),
    "77": (22, 32, "número do documento"),
}


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    campos = CAMPOS_NUMERO.get(registro.tipo)
    if not campos:
        return []
    linha = registro.conteudo
    if registro.tipo == "61" and len(linha) > 2 and linha[2] == "R":
        return []
    if not isinstance(campos, list):
        campos = [campos]

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
                        f"{nome}: {valor!r} não é numérico."
                    ),
                    regra="Número com conteúdo inválido",
                    corrigir=False,
                )
            )
            continue
        if valor == "0" * len(valor):
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro=registro.tipo,
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"{nome}: {valor} — número de documento todo em "
                        f"zeros é inválido no SINTEGRA."
                    ),
                    regra="Número de documento zerado",
                    corrigir=False,
                )
            )

    return itens


plugin = CorretorPlugin(
    id="corretor_numero",
    nome="Corretor de Número de Documento",
    descricao="Identifica números de documento em branco, não numéricos ou todo em zeros nos registros 50, 53, 54, 61, 70, 71, 76 e 77.",
    versao="1.0",
    registros_afetados=["50", "53", "54", "61", "70", "71", "76", "77"],
    analisar=_analisar,
)
