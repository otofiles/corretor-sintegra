from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from core.models import MODOS

COR_CABECALHO = "#12315b"
COR_FUNDO = "#f2f4f7"
COR_CARTAO = "#ffffff"
COR_BORDA = "#dadce0"
COR_PRIMARIA = "#1a73e8"


class JanelaConfiguracoes(tk.Toplevel):
    def __init__(self, master, ctx):
        super().__init__(master)
        self.ctx = ctx
        self.title("Configurações técnicas")
        self.geometry("820x580")
        self.minsize(720, 500)
        self.transient(master)
        self.grab_set()
        self.configure(background=COR_FUNDO)
        self._vars = {}
        self._rotulos = list(MODOS.values())
        self._rotulo_para_chave = {r: c for c, r in MODOS.items()}

        self._montar_geral()
        self._montar_plugins()
        self._montar_rodape()

    def _montar_geral(self):
        frame_geral = ttk.LabelFrame(
            self,
            text="Geral",
            style="Card.TFrame",
            labelanchor="nw",
            padding=14,
        )
        frame_geral.pack(fill="x", padx=16, pady=(16, 8))
        self.var_backup = tk.BooleanVar(value=self.ctx.settings.backup)
        ttk.Checkbutton(
            frame_geral,
            text="Criar backup (.bak) antes de corrigir o arquivo original",
            variable=self.var_backup,
            style="Card.TCheckbutton",
        ).pack(anchor="w", pady=3)
        self.var_relatorio_tecnico = tk.BooleanVar(
            value=self.ctx.settings.exibir_relatorio_tecnico
        )
        ttk.Checkbutton(
            frame_geral,
            text="Exibir o relatório técnico completo após processar",
            variable=self.var_relatorio_tecnico,
            style="Card.TCheckbutton",
        ).pack(anchor="w", pady=3)

    def _montar_plugins(self):
        frame_plugins = ttk.LabelFrame(
            self,
            text="Corretores — comportamento de cada um",
            style="Card.TFrame",
            labelanchor="nw",
            padding=14,
        )
        frame_plugins.pack(fill="both", expand=True, padx=16, pady=8)
        self.corpo = ttk.Frame(frame_plugins, style="Card.TFrame")
        self.corpo.pack(fill="both", expand=True)
        self.atualizar()

    def _montar_rodape(self):
        frame_rodape = ttk.Frame(self, style="Card.TFrame")
        frame_rodape.pack(fill="x", padx=16, pady=8)
        ttk.Button(
            frame_rodape,
            text="Salvar configurações",
            style="Selecionar.TButton",
            command=self._salvar,
        ).pack(side="left")
        ttk.Button(
            frame_rodape,
            text="Recarregar corretores",
            command=self._recarregar,
        ).pack(side="left", padx=8)

    def atualizar(self):
        for child in self.corpo.winfo_children():
            child.destroy()
        self._vars = {}
        if not self.ctx.plugins:
            ttk.Label(
                self.corpo, text="Nenhum corretor encontrado na pasta corretores/."
            ).pack(anchor="w")
            return
        for p in self.ctx.plugins:
            cfg = self.ctx.settings.plugins.get(p.id, {})
            linha = ttk.Frame(self.corpo, style="Card.TFrame")
            linha.pack(fill="x", pady=3)
            var_hab = tk.BooleanVar(value=bool(cfg.get("habilitado", True)))
            var_modo = tk.StringVar(
                value=MODOS.get(cfg.get("modo", "auto_corrigir_e_relatar"), self._rotulos[0])
            )
            ttk.Checkbutton(linha, text=f"{p.nome} — {p.id}", variable=var_hab).pack(side="left")
            ttk.Label(linha, text="  Modo:  ").pack(side="left")
            combo = ttk.Combobox(
                linha, textvariable=var_modo, values=self._rotulos, state="readonly", width=32
            )
            combo.pack(side="left")
            self._vars[p.id] = (var_hab, var_modo)

    def _recarregar(self):
        if self.ctx.aba_processamento.on_recarregar:
            self.ctx.aba_processamento.on_recarregar()
        self.atualizar()

    def _salvar(self):
        for p_id, (var_hab, var_modo) in self._vars.items():
            chave = self._rotulo_para_chave.get(var_modo.get(), "auto_corrigir_e_relatar")
            self.ctx.settings.plugins[p_id] = {"habilitado": var_hab.get(), "modo": chave}
        self.ctx.settings.backup = self.var_backup.get()
        self.ctx.settings.exibir_relatorio_tecnico = self.var_relatorio_tecnico.get()
        self.ctx.settings.salvar()
        messagebox.showinfo("Configurações", "Configurações salvas com sucesso.", parent=self)
