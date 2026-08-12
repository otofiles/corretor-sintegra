from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core.engine import Engine
from core.report import gerar_relatorio_amigavel, gerar_texto, salvar_log_tecnico


class AbaProcessamento(ttk.Frame):
    def __init__(self, parent, ctx):
        super().__init__(parent)
        self.ctx = ctx
        self.on_recarregar = None
        self.on_resultado = None
        self._rodando = False
        self._estado = {"atual": 0, "total": 0, "resultado": None, "texto": "", "erro": None}

        titulo = ttk.Label(self, text="Validação de arquivo SINTEGRA", font=("Segoe UI", 13, "bold"))
        titulo.pack(anchor="w")
        subtitulo = ttk.Label(
            self,
            text="Selecione o arquivo gerado pelo seu sistema e clique em Processar.\n"
            "O programa identifica e corrige erros comuns automaticamente, com backup.",
            justify="left",
        )
        subtitulo.pack(anchor="w", pady=(4, 12))

        frame_arquivo = ttk.LabelFrame(self, text="Arquivo SINTEGRA")
        frame_arquivo.pack(fill="x")
        self.var_arquivo = tk.StringVar()
        ttk.Entry(frame_arquivo, textvariable=self.var_arquivo).pack(
            side="left", fill="x", expand=True, padx=8, pady=8
        )
        ttk.Button(frame_arquivo, text="Selecionar...", command=self._selecionar).pack(
            side="right", padx=8, pady=8
        )

        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(pady=(18, 6))
        self.btn_executar = ttk.Button(
            frame_botoes,
            text="PROCESSAR",
            style="Processar.TButton",
            command=self._executar,
        )
        self.btn_executar.pack(ipadx=28, ipady=6)

        self.progresso = ttk.Progressbar(self, mode="determinate")
        self.progresso.pack(fill="x", padx=4, pady=(14, 4))
        self.lbl_status = ttk.Label(self, text="")
        self.lbl_status.pack(pady=2)

        self.lbl_resumo = ttk.Label(self, text="", justify="left")
        self.lbl_resumo.pack(anchor="w", padx=4, pady=(10, 4))

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
        self.lbl_resumo.config(text="")
        self._estado = {"atual": 0, "total": 0, "resultado": None, "texto": "", "erro": None}

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
        self._exibir_resumo(resultado)
        if self.on_resultado:
            self.on_resultado(resultado, texto_amigavel, texto_tecnico, caminho_log)

    def _exibir_resumo(self, resultado):
        total_corr = sum(s.corrigidos for s in resultado.por_plugin.values())
        total_apont = sum(s.apontados for s in resultado.por_plugin.values())
        total_erros = sum(s.erros for s in resultado.por_plugin.values())
        backup = resultado.backup.name if resultado.backup else "não"
        self.lbl_resumo.config(
            text=(
                f"Registros analisados: {resultado.total_registros}\n"
                f"Corrigidos: {total_corr} | Apontados: {total_apont} | Erros: {total_erros}\n"
                f"Backup criado: {backup}"
            )
        )
