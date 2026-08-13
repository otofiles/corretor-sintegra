from __future__ import annotations

from typing import Dict, List, Set

from core.models import CorretorPlugin, ItemCorrecao, Registro

_POS_NOTA_50 = (45, 51)
_POS_MODELO_50 = (40, 42)
_POS_NOTA_51 = (45, 51)

_MODELO_ESPERADO = "01"
_CABECALHOS: Dict[str, Set[str]] = {}


def _reiniciar_estado() -> None:
    _CABECALHOS.clear()


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    linha = registro.conteudo
    tipo = registro.tipo

    if tipo == "10":
        _reiniciar_estado()
        return []

    if tipo == "50":
        if len(linha) < _POS_MODELO_50[1]:
            return []
        nota = linha[_POS_NOTA_50[0]:_POS_NOTA_50[1]].strip()
        modelo = linha[_POS_MODELO_50[0]:_POS_MODELO_50[1]].strip()
        if nota and modelo:
            _CABECALHOS.setdefault(nota, set()).add(modelo)
        return []

    if tipo == "51":
        if len(linha) < _POS_NOTA_51[1]:
            return []
        nota = linha[_POS_NOTA_51[0]:_POS_NOTA_51[1]].strip()
        if not nota:
            return []
        modelos = _CABECALHOS.get(nota)
        if modelos is None:
            descricao = (
                f"Nota fiscal {nota}: não foi encontrado registro 50 "
                f"(cabeçalho) correspondente para esta nota — o validador do "
                f"Sintegra exige um registro 50 modelo {_MODELO_ESPERADO}."
            )
            regra = "Registro 50 não encontrado para o registro 51"
        elif _MODELO_ESPERADO not in modelos:
            descricao = (
                f"Nota fiscal {nota}: o registro 50 (cabeçalho) correspondente "
                f"está com modelo {', '.join(sorted(modelos))}; o validador do "
                f"Sintegra exige modelo {_MODELO_ESPERADO}."
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
        "Para cada registro 51, verifica se existe um registro 50 (cabeçalho) "
        "da mesma nota com modelo 01, conforme exige o validador do Sintegra. "
        "O registro 51 (documento de transporte) referencia a nota fiscal "
        "(registro 50) pelo número da nota, que pode estar sob CNPJ diferente "
        "do emitente; por isso a busca do cabeçalho é feita pelo número da "
        "nota. Quando não há registro 50 correspondente ou o modelo dele difere "
        "de 01, aponta o erro (não corrige automaticamente)."
    ),
    versao="1.0.5",
    registros_afetados=["50", "51"],
    analisar=_analisar,
)
