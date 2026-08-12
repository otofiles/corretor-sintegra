# 01 - Estrutura dos registros SINTEGRA

Arquivo texto, registros (linhas) de no máximo 126 posições.
Posições informadas aqui são **1-based** (como no manual); em Python subtrair 1.

- Campos **numéricos (N)**: alinhados à direita, zeros à esquerda.
- Campos **alfanuméricos (X)**: alinhados à esquerda, brancos à direita.
- Datas: `AAAAMMDD`. Alíquotas: 4 posições, ex. 17% = `1700`, 25% = `2500`.
- CNPJ/CPF: 14 posições (CPF com zeros à esquerda = 11 dígitos em 14).
- Operações com exterior: CNPJ zerado, IE = `ISENTO`, UF = `EX`.

## Ordem de montagem (classificação)

1. Registro 10 (1ª linha)
2. Registro 11 (2ª linha)
3. 50, 51, 53 (ordem: tipo, depois data)
4. 54 (ordem: CNPJ, série, número, item)
5. 60, 61, 70, 71 (ordem: tipo, depois data)
6. 74, 75 (75 ordenado por código de produto)
7. 76, 85, 86, 88
8. 90 (últimos registros)

Todos os contribuintes devem apresentar os registros **10, 11 e 90**.
Tipos 10, 11 e 90 NÃO são totalizados no 90 (mas contam no total geral).

## Tipos de registro

| Tipo | Descrição |
|------|-----------|
| 10 | Registro mestre do estabelecimento informante |
| 11 | Dados complementares do informante |
| 50 | Total da NF (modelos 1, 1A, 6, 21, 22, 55, 04, 65) quanto ao ICMS |
| 51 | Total da NF quanto ao IPI |
| 53 | Substituição tributária |
| 54 | Itens da NF (mercadoria/produto) |
| 55 | GNRE (pagamentos) |
| 56 | Complementar — veículos automotores novos |
| 57 | Complementar — medicamentos |
| 60 | Cupom Fiscal/ECF (subtipos M, A, D, I, R) |
| 61 | Documentos não emitidos por ECF (modelos 2, 4, 13-16, 21, 65) |
| 70 | Total de NF de serviço de transporte (modelos 7, 8, 9, 10, 11, 26, 57) |
| 71 | Informações da carga transportada |
| 74 | Inventário |
| 75 | Código de produto/serviço |
| 76 | NF de comunicação/telecomunicação (modelos 21/22) — total |
| 77 | Serviços de comunicação/telecomunicação (itens) |
| 85 | Informações de exportação |
| 86 | Informações complementares de exportação |
| 88S/88E | Anotações de lançamento / equivalência de códigos (subtipo na pos. 3) |
| 90 | Totalização do arquivo |

## Registro 10 (mestre)

| # | Campo | Tam | Posição | Formato |
|---|-------|-----|---------|---------|
| 01 | Tipo | 2 | 1-2 | N |
| 02 | CNPJ do informante | 14 | 3-16 | N |
| 03 | IE do informante | 14 | 17-30 | X |
| 04 | Nome do contribuinte | 35 | 31-65 | X |
| 05 | Município | 30 | 66-95 | X |
| 06 | UF | 2 | 96-97 | X |
| 07 | Fax | 10 | 98-107 | N |
| 08 | Data inicial (período) | 8 | 108-115 | N |
| 09 | Data final (período) | 8 | 116-123 | N |
| 10 | Código estrutura (1/2) | 1 | 124 | X |
| 11 | Natureza das operações (1/2/3) | 1 | 125 | X |
| 12 | Finalidade do arquivo (1/2/3/5) | 1 | 126 | X |

Regras: data inicial = 1º dia do mês; data final = último dia do mesmo mês.

## Registro 11

| # | Campo | Tam | Posição | Formato |
|---|-------|-----|---------|---------|
| 01 | Tipo | 2 | 1-2 | N |
| 02 | Logradouro | 34 | 3-36 | X |
| 03 | Número | 5 | 37-41 | N |
| 04 | Complemento | 22 | 42-63 | X |
| 05 | Bairro | 15 | 64-78 | X |
| 06 | CEP | 8 | 79-86 | N |
| 07 | Contato | 28 | 87-114 | X |
| 08 | Telefone | 12 | 115-126 | N |

## Registro 50 (total NF — ICMS)

| # | Campo | Tam | Posição | Formato |
|---|-------|-----|---------|---------|
| 01 | Tipo | 2 | 1-2 | N |
| 02 | CNPJ | 14 | 3-16 | N |
| 03 | IE | 14 | 17-30 | X |
| 04 | Data emissão/recebimento | 8 | 31-38 | N |
| 05 | UF | 2 | 39-40 | X |
| 06 | Modelo | 2 | 41-42 | N |
| 07 | Série | 3 | 43-45 | X |
| 08 | Número | 6 | 46-51 | N |
| 09 | CFOP | 4 | 52-55 | N |
| 10 | Emitente (P/T) | 1 | 56 | X |
| 11 | Valor total | 13 | 57-69 | N |
| 12 | Base de cálculo ICMS | 13 | 70-82 | N |
| 13 | Valor do ICMS | 13 | 83-95 | N |
| 14 | Isenta/não tributada | 13 | 96-108 | N |
| 15 | Outras | 13 | 109-121 | N |
| 16 | Alíquota | 4 | 122-125 | N |
| 17 | Situação (N/S/E/X/2/4) | 1 | 126 | X |

Um registro 50 por combinação (alíquota, CFOP). Cancelada = situação `S`.

## Registro 53 (substituição tributária)

| # | Campo | Tam | Posição | Formato |
|---|-------|-----|---------|---------|
| 01-10 | (igual ao 50 até CFOP/emitente) | | 1-56 | |
| 11 | Base de cálculo ICMS-ST | 13 | 57-69 | N |
| 12 | ICMS retido | 13 | 70-82 | N |
| 13 | Despesas acessórias | 13 | 83-95 | N |
| 14 | Situação | 1 | 96 | X |
| 15 | Código da antecipação | 1 | 97 | X |

## Registro 54 (itens da NF)

| # | Campo | Tam | Posição | Formato |
|---|-------|-----|---------|---------|
| 01 | Tipo | 2 | 1-2 | N |
| 02 | CNPJ | 14 | 3-16 | N |
| 03 | Modelo | 2 | 17-18 | N |
| 04 | Série | 3 | 19-21 | X |
| 05 | Número | 6 | 22-27 | N |
| 06 | CFOP | 4 | 28-31 | N |
| 07 | CST | 3 | 32-34 | X |
| 08 | Nº do item | 3 | 35-37 | N |
| 09 | Código produto | 14 | 38-51 | X |
| 10 | Quantidade (3 dec) | 11 | 52-62 | N |
| 11 | Valor do produto | 12 | 63-74 | N |
| 12 | Desconto/despesa | 12 | 75-86 | N |
| 13 | Base ICMS | 12 | 87-98 | N |
| 14 | Base ICMS-ST | 12 | 99-110 | N |
| 15 | Valor IPI | 12 | 111-122 | N |
| 16 | Alíquota ICMS | 4 | 123-126 | N |

## Registro 60 (cupom/ECF)

- Subtipo na pos. 3 (M/A/D/I/R).
- **60M** (mestre): tipo 1-2, subtipo 3, data 4-11, nº série 12-31, nº eq. 32-34, modelo 35-36, COO inicial 37-42, COO final 43-48, CRZ 49-54, CRO 55-57, venda bruta 58-73, total geral 74-89.
- **60A** (analítico): situação/alíquota 32-35, valor totalizador parcial 36-47.
- **60D** (diário): código produto 32-45, quantidade 46-58, valor 59-74, base ICMS 75-90, situação/alíquota 91-94, ICMS 95-107.
- **60I** (item): modelo 32-33, COO 34-39, nº item 40-42, código 43-56, quantidade 57-69, valor 70-82, base 83-94, alíquota 95-98, ICMS 99-110.
- **60R** (resumo mensal): mês/ano 4-9, código 10-23, quantidade 24-36, valor 37-52, base 53-68, alíquota 69-72.

## Registro 61 (não ECF)

| # | Campo | Tam | Posição | Formato |
|---|-------|-----|---------|---------|
| 01 | Tipo | 2 | 1-2 | N |
| 02-03 | Brancos | 28 | 3-30 | |
| 04 | Data emissão | 8 | 31-38 | N |
| 05 | Modelo | 2 | 39-40 | N |
| 06 | Série | 3 | 41-43 | X |
| 07 | Subsérie | 2 | 44-45 | X |
| 08 | Nº inicial | 6 | 46-51 | N |
| 09 | Nº final | 6 | 52-57 | N |
| 10 | Valor total | 13 | 58-70 | N |
| 11 | Base ICMS | 13 | 71-83 | N |
| 12 | Valor ICMS | 12 | 84-95 | N |
| 13 | Isenta/não trib. | 13 | 96-108 | N |
| 14 | Outras | 13 | 109-121 | N |
| 15 | Alíquota | 4 | 122-125 | N |
| 16 | Branco | 1 | 126 | X |

Modelos aceitos no 61: 02, 04, 07, 13, 14, 15, 16, 21, 65.

## Registro 70 (NF serviço de transporte)

| # | Campo | Tam | Posição | Formato |
|---|-------|-----|---------|---------|
| 01-10 | Tipo/CNPJ/IE/Data/UF/Modelo/Série/Subsérie/Número/CFOP | | 1-55 | |
| 11 | Valor total | 13 | 56-68 | N |
| 12 | Base ICMS | 14 | 69-82 | N |
| 13 | Valor ICMS | 14 | 83-96 | N |
| 14 | Isenta/não trib. | 14 | 97-110 | N |
| 15 | Outras | 14 | 111-124 | N |
| 16 | Frete (1-CIF/2-FOB/0-outros) | 1 | 125 | N |
| 17 | Situação | 1 | 126 | X |

Série: 1 posição (43). Modelos aceitos: 7, 8, 9, 10, 11, 26, 57.

## Registro 71 (carga transportada)

Tipo 1-2, CNPJ tomador 3-16, IE 17-30, data 31-38, UF 39-40, modelo 41-42,
série 43, subsérie 44-45, número 46-51, UF rem/dest 52-53, CNPJ rem/dest
54-67, IE rem/dest 68-81, data NF 82-89, modelo NF 90-91, série NF 92-94,
número NF 95-100, valor total NF 101-114.

## Registro 74 (inventário)

Tipo 1-2, data 3-10, código produto 11-24, quantidade 25-37, valor 38-50,
código de posse 51, CNPJ possuidor 52-65, IE 66-79, UF 80-81.

## Registro 75 (código produto)

Tipo 1-2, data inicial 3-10, data final 11-18, código 19-32, NCM 33-40,
descrição 41-93, unidade 94-99, alíquota IPI 100-104, alíquota ICMS 105-108,
redução base 109-113, base ST 114-126.

## Registro 76 (comunicação/telecomunicação — total)

Tipo 1-2, CNPJ 3-16, IE 17-30, modelo 31-32, série 33-34, subsérie 35-36,
número 37-46, CFOP 47-50, tipo receita 51, data 52-59, UF 60-61,
valor total 62-74, base ICMS 75-87, valor ICMS 88-99, isenta 100-111,
outras 112-123, alíquota 124-125, situação 126.

## Registro 77 (comunicação/telecomunicação — item)

Tipo 1-2, CNPJ 3-16, modelo 17-18, série 19-20, subsérie 21-22, número 23-32,
CFOP 33-36, tipo receita 37, nº item 38-40, código serviço 41-51,
quantidade 52-64, valor 65-76, desconto 77-88, base ICMS 89-100,
alíquota 101-102, CNPJ operadora 103-116, nº terminal 117-126.

## Registro 85 (exportação)

Tipo 1-2, nº declaração 3-13, data declaração 14-21, natureza 22, nº RE 23-34,
data RE 35-42, conhecimento 43-58, data conhecimento 59-66, tipo conhecimento
67-68, país 69-72, reservado 73-80, data averbação 81-88, NF exportação 89-94,
data emissão NF 95-102, modelo 103-104, série 105-107.

## Registro 86 (complementar exportação)

Tipo 1-2, RE 3-14, data RE 15-22, CNPJ remetente 23-36, IE 37-50, UF 51-52,
número NF 53-58, data emissão 59-66, modelo 67-68, série 69-71, código produto
72-85, quantidade 86-96, valor unitário 97-108, valor total 109-120,
relacionamento 121.

## Registro 90 (totalização)

| # | Campo | Tam | Posição | Formato |
|---|-------|-----|---------|---------|
| 01 | Tipo | 2 | 1-2 | N |
| 02 | CNPJ | 14 | 3-16 | N |
| 03 | IE | 14 | 17-30 | X |
| 04 | Tipo a totalizar | 2 | variável | N |
| 05 | Total do tipo | 8 | variável | N |
| ... | (pares 04/05 repetem) | 10 | variável | |
| 04' | Total geral (`99`) | 2 | variável | N |
| 05' | Total geral de registros | 8 | variável | N |
| -- | Nº de registros 90 | 1 | 126 | N |

- O número de pares (tipo,total) é **variável**: só os tipos "utilizados".
- Tipos **10, 11 e 90 não têm par próprio**, mas entram no **total geral**.
- O total geral é informado como um par com tipo **"99"** (Convênio 31/99):
  o campo 04 = `99` e o campo 05 = total de linhas do arquivo.
- Quando houver mais de um registro 90, o "99" (total geral) vai apenas no
  **último**; nos anteriores o totalizador "99" fica zerado (`99` + 8 zeros).
- Campos 01 a 03 (tipo/CNPJ/IE) iguais em todos os registros 90.
- Posição 126 = número de registros 90 do arquivo (1, 2, ...).
- Posições não utilizadas (anteriores à 126) preenchidas com brancos.

### Como ler o 90 (parse prático)

A partir da posição 31 (1-based), ler blocos de 10 (2 = tipo, 8 = total)
enquanto o 2 primeiros forem um tipo de registro válido ou "99". O par com
tipo "99" é o total geral. Exemplo real (arquivo EX1):

```
90 + CNPJ + IE + 50 00000008 + 53 00000003 + 54 00000035
   + 61 00000012 + 75 00000031 + 99 00000092 + ... + 1
```

No exemplo acima: 8+3+35+12+31 = 89 pares de tipos + 10, 11 e 90 = **92**
linhas (o total geral inclui os registros 10, 11 e o próprio 90).
