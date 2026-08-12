from __future__ import annotations

from typing import List, Optional, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro

CAMPOS_ALIQUOTA = {
    "50": (121, 125, "alíquota ICMS", 4),
    "54": (122, 126, "alíquota ICMS", 4),
    "61": (121, 125, "alíquota ICMS", 4),
    "75": [
        (99, 104, "alíquota IPI", 5),
        (104, 108, "alíquota ICMS", 4),
    ],
    "76": (123, 125, "alíquota ICMS", 2),
    "77": (100, 102, "alíquota ICMS", 2),
}


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    campos = CAMPOS_ALIQUOTA.get(registro.tipo)
    if not campos:
        return []
    linha = registro.conteudo
    if registro.tipo == "61" and len(linha) > 2 and linha[2] == "R":
        return []
    if not isinstance(campos, list):
        campos = [campos]

    itens: List[ItemCorrecao] = []
    for inicio, fim, nome, largura in campos:
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
                        f"{nome}: {valor!r} não é numérico (esperado "
                        f"alíquota de {largura} dígitos, ex.: 17% = 1700)."
                    ),
                    regra="Alíquota inválida",
                    corrigir=False,
                )
            )
            continue
        if len(valor) != largura:
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro=registro.tipo,
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"{nome}: {valor} não tem {largura} dígitos "
                        f"(esperado ex.: 17% = 1700)."
                    ),
                    regra="Alíquota com tamanho inválido",
                    corrigir=False,
                )
            )
            continue
        if largura == 4 and int(valor) > 2500:
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro=registro.tipo,
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"{nome}: {valor} (> 2500) ultrapassa o máximo de "
                        f"25% de alíquota."
                    ),
                    regra="Alíquota acima de 25%",
                    corrigir=False,
                )
            )
            continue
        if largura == 2 and int(valor) > 25:
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro=registro.tipo,
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"{nome}: {valor} (> 25) ultrapassa o máximo de "
                        f"25% de alíquota."
                    ),
                    regra="Alíquota acima de 25%",
                    corrigir=False,
                )
            )

    return itens


plugin = CorretorPlugin(
    id="corretor_aliquota",
    nome="Corretor de Alíquotas",
    descricao="Valida o formato e o limite (0-2500) das alíquotas nos registros 50, 54, 61, 75, 76 e 77.",
    versao="1.0",
    registros_afetados=["50", "54", "61", "75", "76", "77"],
    analisar=_analisar,
)
