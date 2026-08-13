from __future__ import annotations

from typing import Dict, List, Set, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro

# Registro 50 (cabeçalho da NF) — posições 0-based conforme Conv. ICMS 57/95
_POS_CNPJ_50 = (2, 16)
_POS_DATA_50 = (30, 38)
_POS_UF_50 = (38, 40)
_POS_MODELO_50 = (40, 42)
_POS_SERIE_50 = (42, 45)
_POS_NOTA_50 = (45, 51)
_POS_CFOP_50 = (51, 55)

# Registro 51 (total NF p/ IPI) — NAO tem campo de modelo; deslocado 2 posições
_POS_CNPJ_51 = (2, 16)
_POS_DATA_51 = (30, 38)
_POS_UF_51 = (38, 40)
_POS_SERIE_51 = (40, 43)
_POS_NOTA_51 = (43, 49)
_POS_CFOP_51 = (49, 53)

_MODELO_ESPERADO = "01"
_CABECALHOS: Dict[Tuple[str, str, str, str, str], Set[str]] = {}


def _chave(nota: str, cfop: str, data: str, serie: str, uf: str) -> Tuple[str, str, str, str, str]:
    return (nota, cfop, data, serie, uf)


def _reiniciar_estado() -> None:
    _CABECALHOS.clear()


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    linha = registro.conteudo
    tipo = registro.tipo

    if tipo == "10":
        _reiniciar_estado()
        return []

    if tipo == "50":
        if len(linha) < _POS_CFOP_50[1]:
            return []
        chave = _chave(
            linha[_POS_NOTA_50[0]:_POS_NOTA_50[1]].strip(),
            linha[_POS_CFOP_50[0]:_POS_CFOP_50[1]].strip(),
            linha[_POS_DATA_50[0]:_POS_DATA_50[1]].strip(),
            linha[_POS_SERIE_50[0]:_POS_SERIE_50[1]].strip(),
            linha[_POS_UF_50[0]:_POS_UF_50[1]].strip(),
        )
        modelo = linha[_POS_MODELO_50[0]:_POS_MODELO_50[1]].strip()
        _CABECALHOS.setdefault(chave, set()).add(modelo)
        return []

    if tipo == "51":
        if len(linha) < _POS_CFOP_51[1]:
            return []
        nota = linha[_POS_NOTA_51[0]:_POS_NOTA_51[1]].strip()
        if not nota:
            return []
        chave = _chave(
            nota,
            linha[_POS_CFOP_51[0]:_POS_CFOP_51[1]].strip(),
            linha[_POS_DATA_51[0]:_POS_DATA_51[1]].strip(),
            linha[_POS_SERIE_51[0]:_POS_SERIE_51[1]].strip(),
            linha[_POS_UF_51[0]:_POS_UF_51[1]].strip(),
        )
        modelos = _CABECALHOS.get(chave)
        if modelos is None:
            descricao = (
                f"Nota fiscal {nota}: não foi encontrado o registro 50 "
                f"(cabeçalho) correspondente a este documento de transporte "
                f"(registro 51). Revise no seu sistema de emissão o CFOP "
                f"informado no cabeçalho da nota (registro 50) e nos itens "
                f"(registro 54), e confira se o modelo do cabeçalho está correto."
            )
            regra = "Registro 50 não encontrado para o registro 51"
        elif _MODELO_ESPERADO not in modelos:
            descricao = (
                f"Nota fiscal {nota}: o registro 50 (cabeçalho) correspondente "
                f"está com modelo {', '.join(sorted(modelos))}; o validador do "
                f"Sintegra exige modelo {_MODELO_ESPERADO}. Revise no seu "
                f"sistema de emissão o CFOP informado no cabeçalho da nota "
                f"(registro 50) e nos itens (registro 54), e confira se o modelo "
                f"do cabeçalho está correto."
            )
            regra = "Modelo do registro 50 difere de 01"
        else:
            return []
        return [
            ItemCorrecao(
                numero_linha=registro.numero_linha,
                tipo_registro="51",
                texto_original=linha,
                confianca="ALTA",
                descricao=descricao,
                regra=regra,
                corrigir=False,
            )
        ]

    return []


plugin = CorretorPlugin(
    id="corretor_registro51_modelo",
    nome="Modelo do cabeçalho (reg. 51 × reg. 50)",
    descricao=(
        "Para cada registro 51 (total de NF para IPI), verifica se existe um "
        "registro 50 (cabeçalho) correspondente pelos campos comuns "
        "(CGC, número da nota, CFOP, data de emissão, série e UF), conforme o "
        "Guia Prático do Convênio ICMS 57/95. O registro 51 não possui campo "
        "de modelo; o validador assume modelo 01, e a ausência de registro 50 "
        "correspondente ou modelo diferente de 01 gera a crítica 'Não "
        "encontrado registro tipo 50 correspondente ou modelo da NF difere de "
        "01'. Aponta o erro (não corrige automaticamente)."
    ),
    versao="1.0.8",
    registros_afetados=["10", "50", "51"],
    analisar=_analisar,
)
