from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core.engine import Engine
from core.report import gerar_relatorio_amigavel, gerar_texto, salvar_log_tecnico


class TelaCliente(ttk.Frame):
    def __init__(self, parent, ctx):
        super().__init__(parent)
        self.ctx = ctx
        self.on_recarregar = None
        self.on_resultado = None
        self.on_buscar_atualizacoes = None
        self._rodando = False
        self._estado = {"atual": 0, "total": 0, "resultado": None, "texto": "",
                        "erro": None}

        self._montar_passo_1()
        self._montar_passo_2()
        self._montar_passo_3()

        self.pack_propagate(False)

    def _montar_passo_1(self):
        card = ttk.LabelFrame(
            self, text="1. Escolha o arquivo SINTEGRA",
            style="Card.TFrame", labelanchor="nw", padding=16,
        )
        card.pack(fill="x")

        ttk.Label(
            card,
            text="Selecione o arquivo de texto (.TXT) gerado pelo seu sistema.",
            style="CardSub.TLabel",
        ).pack(anchor="w")

        linha = ttk.Frame(card, style="Card.TFrame")
        linha.pack(fill="x", pady=(10, 0))
        self.var_arquivo = tk.StringVar()
        entry = ttk.Entry(linha, textvariable=self.var_arquivo)
        entry.pack(side="left", fill="x", expand=True)
        ttk.Button(
            linha, text="Selecionar...", style="Selecionar.TButton",
            command=self._selecionar,
        ).pack(side="right", padx=(8, 0))

    def _montar_passo_2(self):
        card = ttk.LabelFrame(
            self, text="2. Processe o arquivo",
            style="Card.TFrame", labelanchor="nw", padding=16,
        )
        card.pack(fill="x", pady=(16, 0))

        ttk.Label(
            card,
            text="O programa analisa o arquivo e corrige automaticamente os "
            "erros comuns, sempre com backup.",
            style="CardSub.TLabel",
        ).pack(anchor="w")

        linha = ttk.Frame(card, style="Card.TFrame")
        linha.pack(fill="x", pady=(12, 0))
        self.btn_executar = ttk.Button(
            linha, text="PROCESSAR", style="Processar.TButton",
            command=self._executar,
        )
        self.btn_executar.pack(side="left")
        self.lbl_status = ttk.Label(linha, text="", style="Card.TLabel")
        self.lbl_status.pack(side="left", padx=12)

        self.progresso = ttk.Progressbar(card, style="Progresso.TProgressbar")
        self.progresso.pack(fill="x", pady=(14, 0))

    def _montar_passo_3(self):
        self.card_resultado = ttk.Frame(self, style="Resultado.TFrame", padding=16)
        self.lbl_resultado_titulo = ttk.Label(self.card_resultado, style="Resultado.TLabel")
        self.lbl_resultado_titulo.pack(anchor="w")
        self.lbl_resultado_mensagem = ttk.Label(
            self.card_resultado, style="Resultado.TLabel", justify="left", anchor="w",
        )
        self.lbl_resultado_mensagem.pack(anchor="w", pady=(6, 0))
        self.lbl_resumo = ttk.Label(self.card_resultado, style="Resultado.TLabel", justify="left")
        self.lbl_resumo.pack(anchor="w", pady=(10, 0))

    def _selecionar(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo SINTEGRA",
            filetypes=[("Arquivos TXT", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.var_arquivo.set(caminho)

    def _executar(self):
        if self._rodando:
            return
        caminho_txt = self.var_arquivo.get().strip()
        if not caminho_txt:
            messagebox.showwarning("Atenção", "Selecione um arquivo SINTEGRA.")
            return
        caminho = Path(caminho_txt)
        if not caminho.exists():
            messagebox.showerror("Erro", f"Arquivo não encontrado:\n{caminho}")
            return

        self._rodando = True
        self.btn_executar.config(state="disabled")
        self.lbl_status.config(text="Processando...")
        self.progresso["value"] = 0
        self.card_resultado.pack_forget()
        self._estado = {"atual": 0, "total": 0, "resultado": None, "texto": "",
                        "erro": None}

        def worker():
            try:
                engine = Engine(self.ctx.settings, self.ctx.plugins)
                resultado = engine.executar(caminho, progresso=self._progresso_callback)
                nomes = {p.id: p.nome for p in self.ctx.plugins}
                self._estado["resultado"] = resultado
                self._estado["texto"] = gerar_texto(resultado, nomes)
            except Exception as exc:
                self._estado["erro"] = exc

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()
        self._poll()

    def _progresso_callback(self, atual, total):
        self._estado["atual"] = atual
        self._estado["total"] = total

    def _poll(self):
        if self._thread.is_alive():
            total = self._estado["total"] or 1
            valor = min(100, int(self._estado["atual"] / total * 100))
            self.progresso["value"] = valor
            self.lbl_status.config(
                text=f"Processando... {self._estado['atual']} de {self._estado['total']} registros"
            )
            self.after(80, self._poll)
            return

        self.progresso["value"] = 100
        self._rodando = False
        self.btn_executar.config(state="normal")

        if self._estado["erro"]:
            self.lbl_status.config(text="Erro ao processar.")
            messagebox.showerror("Erro", str(self._estado["erro"]))
            return

        resultado = self._estado["resultado"]
        texto_tecnico = self._estado["texto"]
        nomes = {p.id: p.nome for p in self.ctx.plugins}
        texto_amigavel = gerar_relatorio_amigavel(resultado, nomes)
        caminho_log = salvar_log_tecnico(self.ctx.pasta_logs, texto_tecnico)

        self.lbl_status.config(text=f"Concluído. Log técnico salvo em {caminho_log}")
        if self.on_resultado:
            self.on_resultado(resultado, texto_amigavel, texto_tecnico, caminho_log)

    def mostrar_resultado(self, resultado, texto_amigavel):
        total_corr = sum(s.corrigidos for s in resultado.por_plugin.values())
        total_apont = sum(s.apontados for s in resultado.por_plugin.values())
        total_erros = sum(s.erros for s in resultado.por_plugin.values())
        backup = resultado.backup.name if resultado.backup else "não"

        if "Tudo certo" in texto_amigavel:
            self.lbl_resultado_titulo.config(text="✓ Análise concluída", style="ResultadoOk.TLabel")
        else:
            self.lbl_resultado_titulo.config(text="⚠ Arquivo precisa de ajustes", style="ResultadoAviso.TLabel")

        self.lbl_resultado_mensagem.config(text=texto_amigavel)
        self.lbl_resumo.config(
            text=(
                f"Registros analisados: {resultado.total_registros}\n"
                f"Corrigidos: {total_corr}  |  Apontados: {total_apont}  |  Erros: {total_erros}\n"
                f"Backup criado: {backup}"
            )
        )
        self.card_resultado.pack(fill="x", pady=(16, 0))

    def notificar_status(self, msg: str) -> None:
        self.lbl_status.config(text=msg)
