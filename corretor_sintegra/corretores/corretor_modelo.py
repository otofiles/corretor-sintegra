from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro

MODELOS_POR_TIPO: Dict[str, Set[str]] = {
    "50": {"01", "1A", "04", "06", "21", "22", "55", "65"},
    "53": {"01", "1A", "04", "06", "21", "22", "55", "65"},
    "54": {"01", "1A", "04", "06", "21", "22", "55", "65"},
    "61": {"02", "04", "07", "13", "14", "15", "16", "21", "65"},
    "70": {"07", "08", "09", "10", "11", "26", "57", "58", "67"},
    "71": {"07", "08", "09", "10", "11", "26", "57", "58", "67"},
    "74": {"55"},
    "76": {"21", "22"},
    "77": {"21", "22"},
}

CAMPOS_MODELO = {
    "50": (40, 42),
    "53": (40, 42),
    "54": (16, 18),
    "61": (38, 40),
    "70": (40, 42),
    "71": (40, 42),
    "76": (30, 32),
    "77": (16, 18),
}

MODELOS_DESCRICAO = {
    "01": "Nota Fiscal (modelo 1)",
    "1A": "Nota Fiscal Avulsa (modelo 1A)",
    "04": "Nota Fiscal de Produtor",
    "06": "Nota Fiscal/Conta de Energia Elétrica",
    "07": "Nota Fiscal de Serviço de Transporte",
    "08": "Conhecimento de Transporte Rodoviário de Cargas",
    "09": "Conhecimento de Transporte Aquaviário de Cargas",
    "10": "Conhecimento de Transporte Aéreo",
    "11": "Conhecimento de Transporte Ferroviário de Cargas",
    "13": "Bilhete de Passagem Rodoviário",
    "14": "Bilhete de Passagem Aquaviário",
    "15": "Bilhete de Passagem Aéreo",
    "16": "Bilhete de Passagem Ferroviário",
    "21": "NF de Serviço de Comunicação",
    "22": "NF de Serviço de Telecomunicação",
    "26": "Conhecimento de Transporte Multimodal de Cargas",
    "55": "Nota Fiscal Eletrônica (NF-e)",
    "57": "Conhecimento de Transporte Eletrônico (CT-e)",
    "58": "Conhecimento de Transporte Eletrônico para Outros Serviços (CT-e OS)",
    "65": "Nota Fiscal de Consumidor Eletrônica (NFC-e)",
    "67": "CT-e de Outros Serviços (CT-e OS)",
}


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    pos = CAMPOS_MODELO.get(registro.tipo)
    if not pos:
        return []
    inicio, fim = pos
    linha = registro.conteudo
    if len(linha) < fim:
        return []
    if registro.tipo == "61" and len(linha) > 2 and linha[2] == "R":
        return []
    modelo = linha[inicio:fim].strip()
    if not modelo:
        return []
    permitidos = MODELOS_POR_TIPO[registro.tipo]
    if modelo in permitidos:
        return []
    descricao_modelo = MODELOS_DESCRICAO.get(modelo, "desconhecido")
    itens = [
        ItemCorrecao(
            numero_linha=registro.numero_linha,
            tipo_registro=registro.tipo,
            texto_original=linha,
            confianca="ALTA",
            descricao=(
                f"Modelo {modelo} ({descricao_modelo}) não é aceito no "
                f"registro {registro.tipo}. Modelos aceitos: "
                f"{', '.join(sorted(permitidos))}."
            ),
            regra="Modelo inválido",
            corrigir=False,
        )
    ]
    return itens


plugin = CorretorPlugin(
    id="corretor_modelo",
    nome="Corretor de Modelo",
    descricao="Valida se o modelo do documento é aceito para cada tipo de registro (50, 53, 54, 61, 70, 71, 76, 77).",
    versao="1.0",
    registros_afetados=["50", "53", "54", "61", "70", "71", "76", "77"],
    analisar=_analisar,
)
