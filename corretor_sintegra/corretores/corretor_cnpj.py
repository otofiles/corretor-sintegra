from __future__ import annotations

from typing import List, Optional, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro
from core.validacao import (
    dv_cnpj,
    dv_cpf,
    validar_cnpj,
    validar_cpf,
)

CAMPOS_CNPJ = {
    "10": [(2, 16, "CNPJ do informante")],
    "50": [(2, 16, "CNPJ")],
    "53": [(2, 16, "CNPJ")],
    "54": [(2, 16, "CNPJ")],
    "70": [(2, 16, "CNPJ")],
    "71": [
        (2, 16, "CNPJ do tomador"),
        (53, 67, "CNPJ do remetente/destinatário"),
    ],
    "74": [(51, 65, "CNPJ do possuidor")],
    "76": [(2, 16, "CNPJ")],
    "77": [(2, 16, "CNPJ")],
    "86": [(22, 36, "CNPJ do remetente")],
}

_FORMATO_INVALIDO = "INVALIDO"
_TIPO_CNPJ = "CNPJ"
_TIPO_CPF = "CPF"


def _interpretar_campo(campo: str) -> Optional[Tuple[str, str]]:
    if campo.replace(" ", "") == "":
        return None
    if set(campo.replace(" ", "")) == {"0"}:
        return None
    digitos = "".join(c for c in campo if c.isdigit())
    if len(digitos) == 14:
        return _TIPO_CNPJ, digitos
    if len(digitos) == 11:
        return _TIPO_CPF, digitos
    return _FORMATO_INVALIDO, ""


def _corrigir_campo(tipo: str, campo: str, digitos: str) -> Optional[str]:
    if tipo == _TIPO_CNPJ:
        corpo = digitos[:12]
        novo = corpo + dv_cnpj(corpo)
        if novo != digitos and validar_cnpj(novo):
            return novo
        return None
    if tipo == _TIPO_CPF:
        corpo = digitos[:9]
        novo = corpo + dv_cpf(corpo)
        if novo != digitos and validar_cpf(novo):
            padding = campo[: len(campo) - 11]
            return padding + novo
        return None
    return None


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    campos = CAMPOS_CNPJ.get(registro.tipo)
    if not campos:
        return []
    linha = registro.conteudo
    itens: List[ItemCorrecao] = []

    for inicio, fim, nome in campos:
        if len(linha) < fim:
            continue
        campo = linha[inicio:fim]
        interpretado = _interpretar_campo(campo)

        if interpretado is None:
            continue

        tipo, digitos = interpretado

        if tipo == _FORMATO_INVALIDO:
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro=registro.tipo,
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"{nome}: campo com formato inválido "
                        f"({campo!r}). Esperado CNPJ (14 dígitos) ou CPF "
                        f"(11 dígitos)."
                    ),
                    regra="CNPJ/CPF com conteúdo inválido",
                    corrigir=False,
                )
            )
            continue

        if tipo == _TIPO_CNPJ and validar_cnpj(digitos):
            continue
        if tipo == _TIPO_CPF and validar_cpf(digitos):
            continue

        corrigido = _corrigir_campo(tipo, campo, digitos)

        if corrigido is not None:
            texto_corrigido = linha[:inicio] + corrigido + linha[fim:]
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro=registro.tipo,
                    texto_original=linha,
                    texto_corrigido=texto_corrigido,
                    confianca="ALTA",
                    descricao=(
                        f"{nome}: {tipo} {digitos} tem dígito verificador "
                        f"inválido; corrigido para {corrigido} (o corpo do "
                        f"número foi mantido). Confira se o número informado "
                        f"está correto."
                    ),
                    regra=f"DV do {tipo} não confere",
                    corrigir=True,
                )
            )
        else:
            itens.append(
                ItemCorrecao(
                    numero_linha=registro.numero_linha,
                    tipo_registro=registro.tipo,
                    texto_original=linha,
                    confianca="ALTA",
                    descricao=(
                        f"{nome}: {tipo} {digitos} não passou na validação de "
                        f"dígito verificador e não é possível corrigi-lo "
                        f"automaticamente (número provavelmente digitado "
                        f"errado)."
                    ),
                    regra=f"{tipo} inválido",
                    corrigir=False,
                )
            )

    return itens


plugin = CorretorPlugin(
    id="corretor_cnpj",
    nome="Corretor de CNPJ/CPF",
    descricao=(
        "Valida o dígito verificador de CNPJ/CPF nos registros que possuem o "
        "campo (10, 50, 53, 54, 70, 71, 74, 76, 77, 86). Quando apenas o DV "
        "está errado, recalcula e corrige; caso contrário, aponta o erro."
    ),
    versao="1.0",
    registros_afetados=["10", "50", "53", "54", "70", "71", "74", "76", "77", "86"],
    analisar=_analisar,
)
