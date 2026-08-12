from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from core import caminhos
from core.atualizador import Atualizador
from core.plugin_manager import PluginManager
from core.settings import Settings
from core.versao import NOME_APP, VERSAO

from .aba_configuracoes import JanelaConfiguracoes
from .aba_relatorio import JanelaRelatorio
from .tela_cliente import TelaCliente


# Paleta do aplicativo
COR_CABECALHO = "#12315b"
COR_PRIMARIA = "#1a73e8"
COR_PRIMARIA_ESCURA = "#1558b0"
COR_SUCESSO = "#188038"
COR_ATENCAO = "#e8710a"
COR_ERRO = "#d93025"
COR_FUNDO = "#f2f4f7"
COR_CARTAO = "#ffffff"
COR_TEXTO = "#202124"
COR_TEXTO_SUAVE = "#5f6368"
COR_BORDA = "#dadce0"


class AppContext:
    def __init__(self, raiz: Path):
        self.raiz = raiz
        self.pasta_art = raiz / "art"
        self.pasta_corretores_embutidos = raiz / "corretores"
        self.pasta_dados = caminhos.pasta_dados()
        self.pasta_dados.mkdir(parents=True, exist_ok=True)
        self.pasta_logs = self.pasta_dados / "logs"
        self.pasta_logs.mkdir(parents=True, exist_ok=True)
        self.pasta_corretores_atualizados = self.pasta_dados / "corretores"
        self.atualizador = Atualizador()
        self.versao_local = VERSAO
        self.versao_remota = ""
        self.plugin_manager = PluginManager(
            self.pasta_corretores_embutidos,
            pastas_extra=[self.pasta_corretores_atualizados],
        )
        self.plugins = self.plugin_manager.scan()
        self.settings = Settings(self.pasta_dados / "settings.json")
        self.settings.carregar(self.plugins)
        self.resultado = None
        self.ultimo_relatorio = ""
        self.ultimo_amigavel = ""
        self.tem_atualizacao_app = False
        self.ultima_verificacao: str = ""


class Aplicacao(tk.Tk):
    def __init__(self, raiz: Path):
        super().__init__()
        self.atualizacao_em_andamento = False
        self.ctx = AppContext(raiz)
        self.title(NOME_APP)
        self.geometry("880x640")
        self.minsize(760, 560)

        self._configurar_estilos()
        self._montar_cabecalho()

        self.tela_cliente = TelaCliente(self, self.ctx)
        self.tela_cliente.pack(fill="both", expand=True, padx=28, pady=20)

        self.ctx.aba_processamento = self.tela_cliente
        self.tela_cliente.on_recarregar = self._recarregar
        self.tela_cliente.on_resultado = self._mostrar_resultado
        self.tela_cliente.on_buscar_atualizacoes = self.buscar_atualizacoes

        self._exibir_avisos(self.ctx.plugin_manager.avisos)
        self.after(300, self._verificar_atualizacoes_abertura)

    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure("Cabecalho.TFrame", background=COR_CABECALHO)
        estilo.configure(
            "Cabecalho.TLabel",
            background=COR_CABECALHO,
            foreground="#ffffff",
            font=("Segoe UI", 18, "bold"),
        )
        estilo.configure(
            "CabecalhoSub.TLabel",
            background=COR_CABECALHO,
            foreground="#cfe0f5",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Engrenagem.TButton",
            font=("Segoe UI", 14),
            padding=6,
            background=COR_CABECALHO,
            foreground="#ffffff",
            borderwidth=0,
        )
        estilo.map(
            "Engrenagem.TButton",
            background=[("active", "#1a3a66")],
            foreground=[("active", "#ffffff")],
        )
        estilo.configure(
            "Processar.TButton",
            font=("Segoe UI", 14, "bold"),
            padding=(28, 12),
            background=COR_SUCESSO,
            foreground="#ffffff",
            borderwidth=0,
        )
        estilo.map(
            "Processar.TButton",
            background=[("active", "#157a33"), ("disabled", "#a5d6a7")],
            foreground=[("active", "#ffffff"), ("disabled", "#ffffff")],
        )
        estilo.configure(
            "Selecionar.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(16, 10),
            background=COR_PRIMARIA,
            foreground="#ffffff",
            borderwidth=0,
        )
        estilo.map(
            "Selecionar.TButton",
            background=[("active", COR_PRIMARIA_ESCURA)],
            foreground=[("active", "#ffffff")],
        )
        estilo.configure(
            "Atualizar.TButton",
            font=("Segoe UI", 10),
            padding=(10, 6),
            background=COR_PRIMARIA,
            foreground="#ffffff",
            borderwidth=0,
        )
        estilo.map(
            "Atualizar.TButton",
            background=[("active", COR_PRIMARIA_ESCURA)],
            foreground=[("active", "#ffffff")],
        )
        estilo.configure(
            "Card.TFrame",
            background=COR_CARTAO,
            bordercolor=COR_BORDA,
            relief="solid",
            borderwidth=1,
        )
        estilo.configure("Card.TLabel", background=COR_CARTAO, foreground=COR_TEXTO)
        estilo.configure(
            "Card.TCheckbutton",
            background=COR_CARTAO,
            foreground=COR_TEXTO,
            focuscolor=COR_CARTAO,
        )
        estilo.map("Card.TCheckbutton", background=[("active", COR_CARTAO)])
        estilo.configure(
            "CardTitulo.TLabel",
            background=COR_CARTAO,
            foreground=COR_TEXTO,
            font=("Segoe UI", 13, "bold"),
        )
        estilo.configure(
            "CardSub.TLabel",
            background=COR_CARTAO,
            foreground=COR_TEXTO_SUAVE,
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "ResultadoOk.TLabel",
            background=COR_CARTAO,
            foreground=COR_SUCESSO,
            font=("Segoe UI", 14, "bold"),
        )
        estilo.configure(
            "ResultadoAviso.TLabel",
            background=COR_CARTAO,
            foreground=COR_ATENCAO,
            font=("Segoe UI", 14, "bold"),
        )
        estilo.configure(
            "Resultado.TFrame",
            background=COR_CARTAO,
            bordercolor=COR_BORDA,
            relief="solid",
            borderwidth=1,
        )
        estilo.configure("Resultado.TLabel", background=COR_CARTAO, foreground=COR_TEXTO)
        estilo.configure(
            "Progresso.TProgressbar",
            troughcolor=COR_BORDA,
            background=COR_PRIMARIA,
            thickness=14,
        )
        try:
            layout_base = estilo.layout("Horizontal.TProgressbar")
            estilo.layout("Progresso.TProgressbar", layout_base)
        except tk.TclError:
            pass

    def _montar_cabecalho(self):
        cabecalho = ttk.Frame(self, style="Cabecalho.TFrame")
        cabecalho.pack(fill="x")

        img = self._carregar_logo()
        if img is not None:
            lbl_logo = ttk.Label(cabecalho, image=img, style="Cabecalho.TLabel")
            lbl_logo.image = img
            lbl_logo.pack(side="left", padx=(16, 12), pady=12)
        bloco = ttk.Frame(cabecalho, style="Cabecalho.TFrame")
        bloco.pack(side="left", pady=12)
        ttk.Label(bloco, text=NOME_APP, style="Cabecalho.TLabel").pack(anchor="w")
        ttk.Label(
            bloco,
            text=f"Corrija e valide seu arquivo SINTEGRA em poucos passos  •  v{VERSAO}",
            style="CabecalhoSub.TLabel",
        ).pack(anchor="w")

        botoes = ttk.Frame(cabecalho, style="Cabecalho.TFrame")
        botoes.pack(side="right", padx=6, pady=12)
        ttk.Button(
            botoes,
            text="Buscar atualizações",
            style="Atualizar.TButton",
            command=self.buscar_atualizacoes,
        ).pack(side="right", padx=(0, 6))
        ttk.Button(
            botoes,
            text="⚙",
            style="Engrenagem.TButton",
            command=self._abrir_configuracoes,
        ).pack(side="right")

    def _carregar_logo(self):
        png = self.ctx.pasta_art / "ico2.png"
        ico = self.ctx.pasta_art / "ico2.ico"
        if ico.exists():
            try:
                self.iconbitmap(str(ico))
            except Exception:
                pass
        if not png.exists():
            return None
        try:
            return tk.PhotoImage(file=str(png))
        except Exception:
            return None

    def _abrir_configuracoes(self):
        JanelaConfiguracoes(self, self.ctx)

    def _montar_tela_cliente(self):
        pass

    def _recarregar(self):
        self.ctx.plugins = self.ctx.plugin_manager.scan()
        self.ctx.settings.carregar(self.ctx.plugins)
        self._exibir_avisos(self.ctx.plugin_manager.avisos)

    def _mostrar_resultado(self, resultado, texto_amigavel, texto_tecnico, caminho_log):
        self.ctx.resultado = resultado
        self.ctx.ultimo_relatorio = texto_tecnico
        self.ctx.ultimo_amigavel = texto_amigavel
        self.tela_cliente.mostrar_resultado(resultado, texto_amigavel)
        if self.ctx.settings.exibir_relatorio_tecnico:
            JanelaRelatorio(self, self.ctx, texto_tecnico)

    def _exibir_avisos(self, avisos):
        if avisos:
            messagebox.showwarning("Avisos ao carregar corretores", "\n".join(avisos))

    def _verificar_atualizacoes_abertura(self):
        if self.atualizacao_em_andamento:
            return
        self.atualizacao_em_andamento = True
        threading.Thread(target=self._thread_verificar, daemon=True).start()

    def _thread_verificar(self):
        aut = self.ctx.atualizador
        try:
            remota = aut.versao_remota()
        except Exception:
            remota = None
        self.ctx.versao_remota = remota or "indisponível"
        self.ctx.tem_atualizacao_app = (
            caminhos.esta_empacotado()
            and bool(remota)
            and aut.ha_atualizacao(remota)
        )
        self.atualizacao_em_andamento = False
        if self.ctx.tem_atualizacao_app:
            self.after(0, self._avisar_nova_versao)

    def _avisar_nova_versao(self):
        if messagebox.askyesno(
            "Atualização disponível",
            f"Há uma nova versão do Corretor SINTEGRA disponível "
            f"(você tem a {self.ctx.versao_local}). Deseja baixar e aplicar agora?",
            parent=self,
        ):
            self.buscar_atualizacoes()

    def buscar_atualizacoes(self):
        self.tela_cliente.notificar_status("Verificando atualizações...")
        self.atualizacao_em_andamento = True
        threading.Thread(target=self._thread_buscar_completo, daemon=True).start()

    def _thread_buscar_completo(self):
        aut = self.ctx.atualizador
        mensagens: list = []
        try:
            remota = aut.versao_remota()
            self.ctx.versao_remota = remota or "indisponível"
            if remota and aut.ha_atualizacao(remota):
                if not caminhos.esta_empacotado():
                    mensagens.append(
                        f"Nova versão disponível ({remota}). No modo de "
                        "desenvolvimento, atualize o código via git."
                    )
                else:
                    self.after(
                        0,
                        lambda: self.tela_cliente.notificar_status(
                            f"Baixando atualização {remota}..."
                        ),
                    )
                    ok = aut.baixar_e_aplicar(
                        progresso=lambda m: self.after(
                            0, lambda: self.tela_cliente.notificar_status(m)
                        )
                    )
                    if ok:
                        mensagens.append(
                            f"Atualizado para a versão {remota}. O programa será reiniciado."
                        )
                        self.atualizacao_em_andamento = False
                        self.after(
                            0,
                            lambda: messagebox.showinfo(
                                "Atualização concluída", "\n".join(mensagens), parent=self
                            ),
                        )
                        self.after(400, aut.reiniciar)
                        return
                    mensagens.append("Não foi possível baixar a atualização.")
            else:
                mensagens.append(
                    f"Você já tem a versão mais recente ({aut.versao_local()})."
                )
        except Exception as exc:
            mensagens.append(f"Erro ao buscar atualizações: {exc}")
        self.atualizacao_em_andamento = False
        self.after(0, lambda: self.tela_cliente.notificar_status("Pronto."))
        texto = "\n".join(mensagens) if mensagens else "Nenhuma atualização."
        self.after(
            0,
            lambda: messagebox.showinfo("Buscar atualizações", texto, parent=self),
        )
