from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from core.report import gerar_csv


class JanelaRelatorio(tk.Toplevel):
    def __init__(self, master, ctx, texto):
        super().__init__(master)
        self.ctx = ctx
        self.title("Relatório técnico completo")
        self.geometry("920x640")
        self.minsize(720, 480)
        self.transient(master)

        self.text = scrolledtext.ScrolledText(self, wrap="none", font=("Consolas", 9))
        self.text.pack(fill="both", expand=True, padx=8, pady=6)
        hbar = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(xscrollcommand=hbar.set)
        hbar.pack(side="bottom", fill="x")

        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill="x", padx=8, pady=4)
        ttk.Button(frame_botoes, text="Salvar relatório (.txt)", command=self._salvar_txt).pack(
            side="left", padx=4
        )
        ttk.Button(frame_botoes, text="Exportar (.csv)", command=self._salvar_csv).pack(
            side="left", padx=4
        )

        self.text.insert("1.0", texto)

    def _salvar_txt(self):
        if not self.text.get("1.0", "end").strip():
            messagebox.showinfo("Relatório", "Não há relatório para salvar.", parent=self)
            return
        caminho = _ask_save("relatorio.txt", "Arquivo TXT", "*.txt")
        if caminho:
            Path(caminho).write_text(self.text.get("1.0", "end-1c"), encoding="utf-8")
            messagebox.showinfo("Relatório", f"Relatório salvo em:\n{caminho}", parent=self)

    def _salvar_csv(self):
        resultado = self.ctx.resultado
        if resultado is None:
            messagebox.showinfo("Relatório", "Execute o processamento antes de exportar.", parent=self)
            return
        nomes = {p.id: p.nome for p in self.ctx.plugins}
        conteudo = gerar_csv(resultado, nomes)
        caminho = _ask_save("relatorio.csv", "Arquivo CSV", "*.csv")
        if caminho:
            Path(caminho).write_text(conteudo, encoding="utf-8")
            messagebox.showinfo("Relatório", f"CSV salvo em:\n{caminho}", parent=self)


def _ask_save(nome_padrao: str, descricao: str, extensao: str):
    return filedialog.asksaveasfilename(
        defaultextension=extensao,
        filetypes=[(descricao, extensao)],
        initialfile=nome_padrao,
    )
