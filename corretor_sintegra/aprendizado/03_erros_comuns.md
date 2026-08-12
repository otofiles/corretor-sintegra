# 03 - Erros comuns do SINTEGRA e corretores correspondentes

Fonte: erros relatados em fóruns/suporte (Audisoft, Clipp Store, DATACAMP,
SEFAZ), críticas do Validador SINTEGRA e análise dos arquivos de exemplo.

## Erros por categoria

| # | Categoria | Erro detectado | Registro(s) | Corretor |
|---|-----------|----------------|-------------|----------|
| 1 | Cadastro | CNPJ/CPF com dígito verificador inválido | 10, 50, 53, 54, 70, 71, 74, 76, 77, 86 | corretor_cnpj |
| 2 | Cadastro | IE inválida para a UF (DV) | 10, 50, 53, 70, 71, 74, 85, 86 | corretor_ie |
| 3 | Cadastro | UF inexistente (não é sigla válida) | 10, 50, 53, 70, 71, 74, 76, 86 | corretor_uf |
| 4 | Documento | Data inexistente no calendário (ex.: 31/02) | 10, 50, 53, 61, 70, 71, 74, 75, 85, 86 | corretor_data |
| 5 | Documento | Datas do 10 fora do padrão (início ≠ 01, fim ≠ último dia) | 10 | corretor_data |
| 6 | Documento | Data do documento fora do período do 10 | 50, 53, 61, 70, 71, 74, 76 | corretor_data |
| 7 | Documento | CFOP inválido/inexistente (4 posições, dígito inicial inválido) | 50, 53, 54, 70, 76, 77 | corretor_cfop |
| 8 | Documento | CFOP de transporte com modelo de NF-e (55) | 50 | corretor_cfop_transporte_registro50 |
| 9 | Documento | CST inexistente (conteúdo inválido) | 54, 56 | corretor_cst061* |
| 10 | Documento | Modelo de documento não aceito no registro | 50, 53, 54, 61, 70, 71, 76, 77 | corretor_modelo |
| 11 | Documento | Alíquota > 25% ou mal formatada | 50, 54, 61, 75, 76, 77 | corretor_aliquota |
| 12 | Documento | Número/série zerada (NF inválida) | 50, 53, 54, 61, 70, 71, 76, 77 | corretor_numero |
| 13 | Documento | Valor total/base/ICMS negativos ou não numéricos | 50, 53, 54, 61, 70, 71, 74, 76, 77 | corretor_valores |
| 14 | Estrutura | Registro 90: total por tipo divergente | 90 | corretor_registro90 |
| 15 | Estrutura | Registro 90: total geral divergente | 90 | corretor_registro90 |
| 16 | Estrutura | Linha em branco no arquivo | — | corretor_linha_branca |
| 17 | Estrutura | Arquivo não começa com 10 / não termina com 90 | 10, 90 | corretor_estrutura |
| 18 | Relação | 54 sem 50 correspondente (chave) | 50, 54 | pendente (requer arquivo) |
| 19 | Relação | 75 sem produto referenciado | 54, 75 | pendente (requer arquivo) |
| 20 | ECF | Receita 60M ≠ soma 60A | 60 | pendente (requer arquivo) |

\* o `corretor_cst061` cobre especificamente CST 061; o CST genérico pode ser
ampliado ou virar `corretor_cst`.

## Corretores já implementados

| Corretor | O que faz | Tipo |
|----------|-----------|------|
| corretor_ie | Valida/corrige IE por UF (27 validadores) | corrige (alta) / aponta |
| corretor_cst061 | Aponta itens com CST 061 (base 0) | aponta |
| corretor_cfop_transporte_registro50 | Aponta CFOP de transporte com modelo errado (reg. 50) | aponta |
| corretor_cnpj | Valida/corrige DV de CNPJ/CPF (10, 50, 53, 54, 70, 71, 74, 76, 77, 86) | corrige (alta) / aponta |
| corretor_uf | Aponta UF inexistente (10, 50, 53, 55, 70, 71, 74, 76, 86) | aponta |
| corretor_cfop | Aponta CFOP estruturalmente inválido (50, 53, 54, 70, 76, 77); ignora 0000 em anulação | aponta |
| corretor_data | Aponta datas inválidas e fora do período (10, 50, 53, 61, 70, 71, 74, 75, 76, 85, 86); verifica início=01 e fim=último dia no 10 | aponta |
| corretor_aliquota | Aponta alíquota mal formatada ou > 25% (50, 54, 61, 75, 76, 77); IPI do 75 tem 5 posições | aponta |
| corretor_modelo | Aponta modelo não aceito no tipo de registro (50, 53, 54, 61, 70, 71, 76, 77) | aponta |
| corretor_numero | Aponta número de documento não numérico ou todo em zeros (50, 53, 54, 61, 70, 71, 76, 77) | aponta |
| corretor_valores | Aponta campos de valor não numéricos (50, 53, 54, 61, 70, 71, 74, 76, 77) | aponta |
| corretor_registro90 | Confere totalizadores por tipo e total geral (par 99); reconstrói a linha 90 quando divergente; considera múltiplos 90 (total geral só no último) | corrige (alta/média) |

## Observações de layout usadas nos corretores

- Reg 53 NÃO tem campo de alíquota (termine em "código da antecipação", pos 97).
- Reg 75: alíquota IPI em 5 posições (100-104), alíquota ICMS em 4 (105-108).
- Reg 74 (inventário) não tem campo modelo.
- Reg 61R (subtipo R na pos. 3) tem layout de resumo mensal (mês/ano em 4-9);
  os corretores de data/modelo/número/alíquota/valores ignoram o 61R.
- CFOP `0000` é aceito em registros 50/53/70 com situação "4" (anulação).
