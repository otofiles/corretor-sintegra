from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .backup import criar_backup
from .models import (
    CONF_ALTA,
    MODO_AUTO_RELATAR,
    MODO_SOMENTE_AUTOCORRIGIR,
    MODO_SOMENTE_RELATAR,
    CorretorPlugin,
    EstatisticasPlugin,
    ItemCorrecao,
    Registro,
    ResultadoExecucao,
)
from .settings import Settings


def _ler_arquivo(caminho: Path) -> Tuple[List[str], str]:
    dados = caminho.read_bytes()
    enc = None
    for candidato in ("utf-8", "cp1252", "latin-1"):
        try:
            dados.decode(candidato)
            enc = candidato
            break
        except UnicodeDecodeError:
            continue
    if enc is None:
        enc = "latin-1"
    texto = dados.decode(enc)
    partes = texto.split("\n")
    linhas = [parte + "\n" for parte in partes[:-1]]
    if partes and partes[-1] != "":
        linhas.append(partes[-1])
    return linhas, enc


class Engine:
    def __init__(self, settings: Settings, plugins: List[CorretorPlugin]):
        self.settings = settings
        self.plugins = plugins

    def executar(
        self,
        caminho: Path,
        progresso: Optional[Callable[[int, int], None]] = None,
    ) -> ResultadoExecucao:
        por_tipo: Dict[str, List[CorretorPlugin]] = {}
        ativos: List[CorretorPlugin] = []
        for p in self.plugins:
            cfg = self.settings.plugins.get(p.id, {})
            if not cfg.get("habilitado", True):
                continue
            ativos.append(p)
            for tipo in p.registros_afetados:
                por_tipo.setdefault(tipo, []).append(p)

        linhas, enc = _ler_arquivo(caminho)
        registros: List[Registro] = []
        for numero, raw in enumerate(linhas, 1):
            conteudo = raw.rstrip("\r\n")
            registros.append(
                Registro(numero, conteudo[:2], conteudo, raw[len(conteudo):])
            )

        total = len(registros)
        itens: List[ItemCorrecao] = []
        aplicados: List[ItemCorrecao] = []
        linhas_corrigidas: Dict[int, str] = {}
        por_plugin: Dict[str, EstatisticasPlugin] = {
            p.id: EstatisticasPlugin() for p in self.plugins
        }

        for reg in registros:
            for p in por_tipo.get(reg.tipo, []):
                try:
                    resultado = p.analisar(reg) or []
                except Exception:
                    por_plugin[p.id].erros += 1
                    continue
                for item in resultado:
                    item.plugin = p.id
                    por_plugin[p.id].total += 1
                    self._tratar(item, por_plugin[p.id], linhas_corrigidas, itens, aplicados)
            if progresso and reg.numero_linha % 200 == 0:
                progresso(reg.numero_linha, total)

        backup: Optional[Path] = None
        if linhas_corrigidas:
            if self.settings.backup:
                backup = criar_backup(caminho)
            with caminho.open("wb") as f:
                for reg in registros:
                    novo = linhas_corrigidas.get(reg.numero_linha)
                    if novo is not None:
                        f.write((novo + reg.quebra_linha).encode(enc, errors="replace"))
                    else:
                        f.write((reg.conteudo + reg.quebra_linha).encode(enc, errors="replace"))

        return ResultadoExecucao(
            caminho=caminho,
            backup=backup,
            total_registros=total,
            total_plugins=len(ativos),
            itens=itens,
            itens_aplicados=aplicados,
            por_plugin=por_plugin,
        )

    def _tratar(
        self,
        item: ItemCorrecao,
        stats: EstatisticasPlugin,
        linhas_corrigidas: Dict[int, str],
        itens: List[ItemCorrecao],
        aplicados: List[ItemCorrecao],
    ) -> None:
        cfg = self.settings.plugins.get(item.plugin, {})
        modo = cfg.get("modo", MODO_AUTO_RELATAR)
        reportar = modo in (MODO_AUTO_RELATAR, MODO_SOMENTE_RELATAR)
        auto = modo in (MODO_AUTO_RELATAR, MODO_SOMENTE_AUTOCORRIGIR)
        pode_aplicar = (
            auto
            and item.corrigir
            and item.confianca == CONF_ALTA
            and item.texto_corrigido is not None
        )
        if pode_aplicar and item.numero_linha not in linhas_corrigidas:
            linhas_corrigidas[item.numero_linha] = item.texto_corrigido
            aplicados.append(item)
            stats.corrigidos += 1
            if reportar:
                itens.append(item)
            return
        if reportar:
            itens.append(item)
            stats.apontados += 1
