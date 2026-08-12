from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro
from core.validacao import TIPOS_REGISTRO

TIPOS_COM_PARCELAS = sorted(
    t for t in TIPOS_REGISTRO if t not in ("10", "11", "90")
)

_ESTADO: Dict[str, object] = {
    "contagem": Counter(),
    "90_processados": 0,
    "total_90": 1,
}
_CONFIAVEL: Dict[str, bool] = {"viu_10": False}


def _reiniciar_estado() -> None:
    _ESTADO["contagem"] = Counter()
    _ESTADO["90_processados"] = 0
    _ESTADO["total_90"] = 1
    _CONFIAVEL["viu_10"] = False


def _extrair_pares_90(linha: str) -> Optional[Tuple[Dict[str, int], int]]:
    if len(linha) < 30:
        return None
    pos = 30
    pares: Dict[str, int] = {}
    total_geral: Optional[int] = None
    while pos + 10 <= len(linha):
        bloco = linha[pos:pos + 10]
        tipo = bloco[:2]
        total = bloco[2:10]
        if tipo == "99":
            if total.isdigit():
                total_geral = int(total)
            pos += 10
            break
        if tipo not in TIPOS_REGISTRO or not total.isdigit():
            break
        pares[tipo] = int(total)
        pos += 10
    return pares, total_geral if total_geral is not None else -1


def _montar_linha_90(
    original: str, pares: Dict[str, int], total_geral: int
) -> str:
    base = original[:30].rstrip()
    base = base.ljust(30)
    partes: List[str] = [base]
    for tipo in TIPOS_COM_PARCELAS:
        if pares.get(tipo, 0) > 0:
            partes.append(f"{tipo}{pares[tipo]:08d}")
    partes.append(f"99{total_geral:08d}")
    corpo = "".join(partes)
    corpo = corpo.ljust(125)
    return corpo + "1"


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    linha = registro.conteudo

    if registro.tipo == "10":
        _reiniciar_estado()
        _CONFIAVEL["viu_10"] = True
        _ESTADO["contagem"]["10"] += 1
        return []

    if registro.tipo == "90":
        _ESTADO["90_processados"] = int(_ESTADO["90_processados"]) + 1
        total_90 = 1
        if len(linha) >= 126 and linha[125].isdigit():
            total_90 = int(linha[125]) or 1
        _ESTADO["total_90"] = total_90
        eh_ultimo = int(_ESTADO["90_processados"]) >= total_90

        pares, total_geral = _extrair_pares_90(linha)
        if pares is None:
            return [
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro="90",
                    texto_original=linha,
                    confianca="ALTA",
                    descricao="Registro 90 ilegível (não foi possível ler os totalizadores).",
                    regra="Totalização ilegível",
                    corrigir=False,
                )
            ]

        contagem = _ESTADO["contagem"]
        total_real = sum(contagem.values()) + int(_ESTADO["90_processados"])

        divergencias: List[str] = []
        for tipo in sorted(set(contagem) | set(pares)):
            if tipo in ("10", "11", "90"):
                continue
            real = contagem.get(tipo, 0)
            declarado = pares.get(tipo, 0)
            if real != declarado:
                divergencias.append(
                    f"tipo {tipo}: declarado {declarado}, encontrado {real}"
                )

        if eh_ultimo and total_geral >= 0 and total_geral != total_real:
            divergencias.append(
                f"total geral: declarado {total_geral}, encontrado {total_real}"
            )

        if not divergencias:
            return []

        novo_pares = {
            t: _ESTADO["contagem"].get(t, 0) for t in TIPOS_COM_PARCELAS
        }
        corrigido = _montar_linha_90(linha, novo_pares, total_real)
        confianca = "ALTA" if _CONFIAVEL["viu_10"] else "MEDIA"

        return [
            ItemCorrecao(
                numero_linha=registro.numero_linha,
                tipo_registro="90",
                texto_original=linha,
                texto_corrigido=corrigido,
                confianca=confianca,
                descricao=(
                    "Totalização do registro 90 não confere com os registros "
                    "do arquivo: " + "; ".join(divergencias) + ". "
                    "Registro 90 reconstruído com as contagens reais."
                ),
                regra="Total de registros não confere",
                corrigir=True,
            )
        ]

    if _CONFIAVEL["viu_10"]:
        _ESTADO["contagem"][registro.tipo] += 1
    return []


plugin = CorretorPlugin(
    id="corretor_registro90",
    nome="Corretor de Totalização (registro 90)",
    descricao=(
        "Conta os registros por tipo ao longo do arquivo e valida os "
        "totalizadores do registro 90 (pares tipo/total e total geral com "
        "código 99). Quando a contagem não confere, reconstrói a linha 90."
    ),
    versao="1.0",
    registros_afetados=[
        "10", "11", "50", "51", "53", "54", "55", "56", "57", "60", "61",
        "70", "71", "74", "75", "76", "77", "85", "86", "88", "90",
    ],
    analisar=_analisar,
)
