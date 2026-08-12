from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

CONF_ALTA = "ALTA"
CONF_MEDIA = "MEDIA"
CONF_BAIXA = "BAIXA"

MODO_AUTO_RELATAR = "auto_corrigir_e_relatar"
MODO_SOMENTE_AUTOCORRIGIR = "somente_auto_corrigir"
MODO_SOMENTE_RELATAR = "somente_relatar"

MODOS = {
    MODO_AUTO_RELATAR: "Auto corrigir + gerar relatório",
    MODO_SOMENTE_AUTOCORRIGIR: "Somente autocorrigir",
    MODO_SOMENTE_RELATAR: "Somente gerar relatório",
}


@dataclass
class Registro:
    numero_linha: int
    tipo: str
    conteudo: str
    quebra_linha: str = ""


@dataclass
class ItemCorrecao:
    numero_linha: int
    tipo_registro: str
    texto_original: str
    texto_corrigido: Optional[str] = None
    confianca: str = CONF_BAIXA
    descricao: str = ""
    regra: str = ""
    corrigir: bool = False
    plugin: str = ""


@dataclass
class CorretorPlugin:
    id: str
    nome: str
    descricao: str
    versao: str
    registros_afetados: List[str]
    analisar: Callable[[Registro], List[ItemCorrecao]]


@dataclass
class EstatisticasPlugin:
    total: int = 0
    corrigidos: int = 0
    apontados: int = 0
    erros: int = 0


@dataclass
class ResultadoExecucao:
    caminho: Path
    backup: Optional[Path]
    total_registros: int
    total_plugins: int
    itens: List[ItemCorrecao]
    itens_aplicados: List[ItemCorrecao]
    por_plugin: Dict[str, EstatisticasPlugin]
