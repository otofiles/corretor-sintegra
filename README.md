# Corretor SINTEGRA

Programa que **analisa e corrige arquivos SINTEGRA** (Convênio ICMS 57/95) gerados
pelo seu sistema. Ele encontra os erros mais comuns e já corrige a maior parte
sozinho, sempre com um backup do seu arquivo original.

---

## Baixar

Clique no link abaixo e salve o arquivo no seu computador:

➡️ **[Baixar Corretor SINTEGRA (última versão)](https://github.com/otofiles/corretor-sintegra/releases/latest/download/CorretorSINTEGRA.exe)**

Funciona em qualquer PC com Windows (32 ou 64 bits) e não precisa de instalação.

---

## Como usar

1. **Abra o programa** dando dois cliques no `CorretorSINTEGRA.exe`.
   - Na primeira vez, ele baixa o restante dos arquivos sozinho (precisa de internet).
   - Nas próximas aberturas, já se atualiza automaticamente.

2. **Escolha o arquivo SINTEGRA**
   - Clique em **Selecionar...** e escolha o arquivo de texto (`.TXT`) que o seu sistema gerou.

3. **Clique em PROCESSAR**
   - O programa varre o arquivo, corrige os erros automaticamente e faz um backup.

4. **Veja o resultado**
   - Aparece um resumo com: registros analisados, corrigidos, apontados, erros e o
     backup criado. Se algo precisar de atenção, o programa avisa o que fazer.

Pronto. Para um novo arquivo, é só repetir do passo 2.

> **Configurações e relatório técnico:** no canto superior direito há uma engrenagem ⚙
> (uso do técnico). O botão **Buscar atualizações** também fica ali e força a verificação
> de novas versões.

---

## Perguntas frequentes

**Apareceu "Windows protegeu seu PC".**
O programa é gratuito e não é assinado, então o Windows avisa. Clique em
*Mais informações* e depois em *Executar mesmo assim*. Não prejudica o seu computador.

**Precisa de internet?**
Só na primeira abertura (para baixar o programa) e quando há uma atualização nova.
Depois disso roda normalmente.

**Onde fica meu arquivo original?**
O programa cria um backup automático (arquivo `.bak`) antes de qualquer correção.
Nada é alterado sem segurança.

**Como atualizo?**
É sozinho: basta abrir o programa. Se quiser forçar, use o botão *Buscar atualizações*.

---

<details>
<summary><b>Para técnicos</b></summary>

### Visão geral

O projeto usa um **executável magro com auto-atualização via GitHub**: o `CorretorSINTEGRA.exe`
quase nunca muda. Toda a interface e os corretores são baixados do repositório na
primeira execução e nas atualizações.

- `launcher.py` vira o `.exe` (PyInstaller, apenas o esqueleto).
- Ao abrir, o `.exe` consulta a *última release* do GitHub (`otofiles/corretor-sintegra`),
  compara com `%LOCALAPPDATA%\CorretorSINTEGRA\versao.txt` e, se houver novidade (ou for a
  primeira vez), baixa `corretor_sintegra.zip`, extrai para
  `%LOCALAPPDATA%\CorretorSINTEGRA\corretor_sintegra` e grava `versao.txt`.
- O botão **Buscar atualizações** força a verificação, baixa e reinicia.

O repositório configurado está na constante `REPOSITORIO` em `launcher.py` e em
`corretor_sintegra/core/atualizador.py`.

### Estrutura

```
CorretorSINTEGRA/
├── launcher.py              # esqueleto que vira o .exe (auto-update)
├── build/
│   ├── build_pacote.py      # gera dist/corretor_sintegra.zip
│   └── build_exe.py         # gera dist/CorretorSINTEGRA.exe
├── corretor_sintegra/       # pacote baixado/atualizado pelo app
│   ├── main.py              # ponto de entrada do app
│   ├── core/                # núcleo (engine, caminhos, atualizador...)
│   ├── ui/                  # interface (Tkinter)
│   ├── corretores/          # plugins de correção (arquitetura em plugins)
│   ├── art/                 # ícones
│   └── data/                # dados padrão (tabela CFOP)
└── README.md
```

### Gerando pacote e executável

```powershell
python build/build_pacote.py     # dist/corretor_sintegra.zip (~39 arquivos)
python build/build_exe.py        # dist/CorretorSINTEGRA.exe
```

O nome do asset do pacote **precisa ser exatamente** `corretor_sintegra.zip`.

### Como funciona

O Corretor SINTEGRA confere o arquivo conforme as regras do Convênio ICMS 57/95 e
ajuda a deixá-lo pronto para o Validador do Sintegra:

- **Verifica cada registro** do arquivo contra as regras da escrituração (CNPJ/IE,
  CFOP, datas, CST, totalização do arquivo etc.).
- **Corrige automaticamente** o que tem certeza (por exemplo, dígitos verificadores
  e totais do arquivo), sempre com backup do original antes de alterar qualquer coisa.
- **Aponta o que precisa de atenção** com uma orientação clara de onde olhar no seu
  sistema (por exemplo, "localize a nota X e confira a IE"), sem mexer no que não
  tem certeza.
- **Se atualiza sozinho**: quando há nova versão, o programa busca e aplica a
  atualização automaticamente.

Você só escolhe o arquivo, clica em PROCESSAR e segue o que aparece na tela.

### Testes e checagem (modo desenvolvimento)

Do diretório `corretor_sintegra`:

```powershell
python main.py                                  # abrir a interface (sem .exe)
python -m unittest discover -s testes -v        # rodar testes
python -m compileall -q corretor_sintegra       # checar sintaxe
```

### Segurança

O download usa HTTPS do GitHub e o pacote é extraído para uma pasta do usuário. Não há
execução de código fora do pacote oficial da release. Para ambiente corporativo, use um
fork privado ou self-host alterando a constante `REPOSITORIO`.

</details>
