from __future__ import annotations

from typing import Dict, List, Set

from core.models import CorretorPlugin, ItemCorrecao, Registro

_POS_CNPJ_50 = (2, 16)
_POS_NOTA_50 = (45, 51)
_POS_CFOP_50 = (51, 55)
_POS_CNPJ_54 = (2, 16)
_POS_NOTA_54 = (21, 27)
_POS_CFOP_54 = (27, 31)

_CABECALHOS: Dict[tuple, Set[str]] = {}


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
        cnpj = linha[_POS_CNPJ_50[0]:_POS_CNPJ_50[1]].strip()
        nota = linha[_POS_NOTA_50[0]:_POS_NOTA_50[1]].strip()
        cfop = linha[_POS_CFOP_50[0]:_POS_CFOP_50[1]].strip()
        if cnpj and nota and cfop:
            _CABECALHOS.setdefault((cnpj, nota), set()).add(cfop)
        return []

    if tipo == "54":
        if len(linha) < _POS_CFOP_54[1]:
            return []
        cnpj = linha[_POS_CNPJ_54[0]:_POS_CNPJ_54[1]].strip()
        nota = linha[_POS_NOTA_54[0]:_POS_NOTA_54[1]].strip()
        cfop = linha[_POS_CFOP_54[0]:_POS_CFOP_54[1]].strip()
        if not cfop or cfop == "0000":
            return []
        chave = (cnpj, nota)
        cabecalhos = _CABECALHOS.get(chave)
        if cabecalhos is None:
            descricao = (
                f"Nota fiscal {nota}: o item com CFOP {cfop} não possui "
                f"registro 50 (cabeçalho) correspondente na nota — possível "
                f"importação incorreta."
            )
            regra = "Item sem registro 50 correspondente"
        elif cfop not in cabecalhos:
            descricao = (
                f"Nota fiscal {nota}: o CFOP {cfop} do item não corresponde "
                f"a nenhum CFOP do cabeçalho (registro 50) da nota "
                f"({', '.join(sorted(cabecalhos))}) — possível importação "
                f"incorreta."
            )
            regra = "CFOP do item não confere com o cabeçalho"
        else:
            return []
        return [
            ItemCorrecao(
                numero_linha=registro.numero_linha,
                tipo_registro="54",
                texto_original=linha,
                confianca="ALTA",
                descricao=descricao,
                regra=regra,
                corrigir=False,
            )
        ]

    return []


plugin = CorretorPlugin(
    id="corretor_cfop_item_registro50",
    nome="Consistência de CFOP (item × cabeçalho)",
    descricao=(
        "Verifica se o CFOP de cada item (registro 54) confere com algum "
        "CFOP do cabeçalho (registro 50) da mesma nota. Itens cujo CFOP não "
        "tem registro 50 correspondente na nota indicam importação "
        "incorreta e são apontados (não corrigidos automaticamente)."
    ),
    versao="1.0",
    registros_afetados=["50", "54"],
    analisar=_analisar,
)
