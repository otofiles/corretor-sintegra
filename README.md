# Corretor SINTEGRA

Aplicativo em Python + Tkinter (só biblioteca padrão) que analisa e corrige
arquivos SINTEGRA (Convênio ICMS 57/95). Correções automáticas somente com
confiança alta e sempre com backup `.bak`.

Este projeto usa um **executável magro com auto-atualização via GitHub**: o
`.exe` quase nunca muda. Toda a interface e os corretores são baixados do
repositório na primeira execução e nas atualizações. Assim você não precisa
distribuir um novo instalador a cada correção.

---

## 1. Como funciona o auto-updater (resumo)

- `launcher.py` vira o `CorretorSINTEGRA.exe` (PyInstaller, apenas o "esqueleto").
- Ao abrir, o `.exe` consulta a *última release* do GitHub
  (`otofiles/corretor-sintegra`) e compara a versão com a que já está em
  `%LOCALAPPDATA%\CorretorSINTEGRA`.
- Se houver versão nova (ou for a primeira vez), ele baixa o pacote
  `corretor_sintegra.zip`, extrai para
  `%LOCALAPPDATA%\CorretorSINTEGRA\corretor_sintegra` e grava `versao.txt`.
- Depois carrega o app a partir desse pacote e abre a tela.
- O botão **"Buscar atualizações"** (canto superior direito) força a verificação,
  baixa se houver novidade e reinicia o programa.

> O repositório configurado está em `launcher.py` e em
> `corretor_sintegra/core/atualizador.py` (constante `REPOSITORIO`).
> Troque `otofiles/corretor-sintegra` pelo seu usuário/repo ao publicar.

---

## 2. Pré-requisitos

- Python **3.11** (32 bits neste projeto) — https://www.python.org
- `PyInstaller` (já instalado): `pip install pyinstaller`
- `Git` (já instalado). No Windows: https://git-scm.com
- Conta no GitHub e o repositório `otofiles/corretor-sintegra` criado (público).

---

## 3. Estrutura do projeto

```
CorretorSINTEGRA/
├── launcher.py                 # esqueleto que vira o .exe (auto-update)
├── build/
│   ├── build_pacote.py         # gera dist/corretor_sintegra.zip
│   └── build_exe.py            # gera dist/CorretorSINTEGRA.exe
├── corretor_sintegra/          # pacote baixado/atualizado pelo app
│   ├── main.py                 # ponto de entrada do app
│   ├── core/                   # núcleo (engine, caminhos, atualizador...)
│   ├── ui/                     # interface (Tkinter)
│   ├── corretores/             # plugins de correção (arquitetura em plugins)
│   ├── art/                    # ícones (ico2.ico / ico2.png)
│   └── data/                   # dados padrão (exemplos, CFOP)
├── exemplos para estudar/      # arquivos usados nos testes
├── dist/                       # saída de build (ignorado pelo git)
├── .gitignore
└── README.md
```

Dados do usuário (logs, `settings.json`, corretores extras) ficam em
`%LOCALAPPDATA%\CorretorSINTEGRA\dados` — separados do pacote, para não serem
perdidos nas atualizações.

---

## 4. Subindo o projeto para o GitHub (primeira vez)

1. Crie o repositório no GitHub: `otofiles/corretor-sintegra` (público).
   **Não** marque "Add a README" (já temos um).

2. No terminal, dentro da pasta `CorretorSINTEGRA`:

   ```powershell
   git init
   git branch -M main
   git remote add origin https://github.com/otofiles/corretor-sintegra.git
   git add .
   git commit -m "Versao inicial 1.0.0 com auto-updater via GitHub"
   git push -u origin main
   ```

   (Se o Git pedir identificação, configure localmente:
   `git config user.name "otofiles"` e
   `git config user.email "otofiles@users.noreply.github.com"`.)

---

## 5. Gerando o pacote e o executável

### Pacote (o que o auto-updater baixa)

```powershell
python build/build_pacote.py
```

Gera `dist/corretor_sintegra.zip` (com 38 arquivos, ~110 KB). O nome do asset
**precisa ser exatamente** `corretor_sintegra.zip`.

### Executável (só na primeira vez e quando mudar o launcher)

```powershell
python build/build_exe.py
```

Gera `dist/CorretorSINTEGRA.exe` com o ícone `art/ico2.ico` e informações de
versão profissionais (sem ícone/metadata de compilação do Python).

> Dica: para testar o `.exe` localmente sem o GitHub, defina as variáveis de
> ambiente `CORRETOR_API_URL` e `CORRETOR_ASSET_URL` apontando para um servidor
> local que sirva o JSON da release e o zip.

---

## 6. Lançando uma nova versão (release)

Sempre que quiser disponibilizar correções ou melhorias para os usuários:

1. **Bump de versão** — edite `corretor_sintegra/core/versao.py`:
   ```python
   VERSAO = "1.0.1"
   ```
2. Gere o pacote: `python build/build_pacote.py`
3. Faça o commit e o push das mudanças de código:
   ```powershell
   git add .
   git commit -m "Correcoes da versao 1.0.1"
   git push
   ```
4. Crie a **Release** no GitHub:
   - Vá em **Releases → New release**.
   - Tag: `v1.0.1` (atenção ao prefixo `v`).
   - Título: `v1.0.1`.
   - Anexe o arquivo `dist/corretor_sintegra.zip` como asset
     (**o nome do asset deve ser `corretor_sintegra.zip`**).
   - Publish release.

Pronto. Na próxima abertura, o `.exe` de qualquer usuário detecta a nova release,
baixa o pacote e atualiza sozinho. **Não é preciso redistribuir o .exe.**

### Adicionar um novo corretor

1. Crie `corretor_sintegra/corretores/corretor_novo.py` expondo um objeto
   `plugin` da classe `CorretorPlugin` (ver os corretores existentes).
2. Bump de versão (item 1 acima) e publique a release (itens 2–4).
3. O app aparece automaticamente para todos os usuários na próxima verificação.

---

## 7. Comandos úteis (modo desenvolvimento)

Do diretório `corretor_sintegra`:

```powershell
# Abrir a interface (modo dev, sem .exe)
python main.py

# Rodar os testes
python -m unittest discover -s testes -v

# Checar sintaxe de todo o projeto
python -m compileall -q corretor_sintegra
```

---

## 8. Solução de problemas

- **"Sem conexão / não foi possível baixar o aplicativo" na primeira abertura:**
  o repositório ainda não tem nenhuma *release* com o asset
  `corretor_sintegra.zip`. Crie a release (seção 6). O `.exe` só funciona após
  a primeira release existir.
- **Atualização não aparece:** confirme que a tag da release tem o prefixo `v`
  (ex.: `v1.0.1`) e que o asset se chama exatamente `corretor_sintegra.zip`.
- **Quer forçar refazer o download:** apague a pasta
  `%LOCALAPPDATA%\CorretorSINTEGRA`. O app baixará tudo de novo na próxima
  abertura.
- **Testes com erro de arquivo de exemplo:** a pasta `exemplos para estudar`
  deve estar em `CorretorSINTEGRA/exemplos para estudar`.

---

## 9. Segurança

O download usa HTTPS do GitHub e o pacote é extraído para uma pasta do usuário.
Não há execução de código fora do pacote oficial da release. Para ambiente
corporativo, você pode usar um fork privado ou self-host alterando a constante
`REPOSITORIO` em `launcher.py` / `core/atualizador.py`.
