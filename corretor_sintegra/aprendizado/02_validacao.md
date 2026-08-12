# 02 - Validação SINTEGRA

Como o **Validador SINTEGRA** (programa oficial distribuído pelas SEFAZ,
baseado no Convênio ICMS 57/95) valida um arquivo. Isso é a base do que os
corretores deste projeto detectam.

## Fluxo de validação

1. **Formato**: registros de no máximo 126 posições; numéricos alinhados à
   direita com zeros; alfanuméricos alinhados à esquerda com brancos; sem
   linhas em branco.
2. **Montagem/ordem**: arquivo começa com 10, segue com 11, e termina com 90
   (os "últimos registros"). Blocos de registros em ordem de classificação
   (tipo, depois data etc.).
3. **Consistência de conteúdo**: CNPJ/IE válidos, datas existentes e dentro
   do período, UFs válidas, CFOPs válidos, CST válido, modelos coerentes,
   somas batem (50↔54, 60 M/A, 90 totalizadores).
4. **Resultado**: aceito / aceito com advertências / rejeitado.

## Regras-chave que o validador aplica

### Registro 10
- Data inicial deve ser **dia 01** do mês.
- Data final deve ser o **último dia** do mesmo mês.
- Finalidade: apenas 1 arquivo com finalidade 1 (normal) por período.
- CNPJ do informante válido; IE válida para a UF.

### Período do arquivo
- Todas as datas de emissão/recebimento dos documentos devem estar
  **compreendidas no mês** informado no registro 10.
- Entradas: data de **recebimento**; saídas: data de **emissão**.

### Registros 50/54 (notas fiscais)
- Para cada registro 50 deve existir registro 54 correspondente (e vice-versa),
  com a MESMA chave: CGC/MF, Modelo, Série, Subsérie, Número, **CFOP e
  alíquota** exatamente iguais. Erro típico: "Não encontrado registro 50
  correspondente" (ex.: 54 com alíquota zerada e 50 com 1700).
- Soma dos itens (54) = totais do 50 (valor total, base, ICMS, isenta, outras).
- Modelo aceito no 50: 01, 1A, 04, 06, 21, 22, 55 (e 65 em versões novas).
- Situação (pos. 126): N, S, E, X, 2, 4. Cancelada = S.
- CFOP válido; CST válido (conteúdo inexistente = erro).
- UF válida; IE válida para a UF (e, quando possível, IE confere com o CNPJ).

### Registro 61
- Modelos aceitos: 02, 04, 07, 13, 14, 15, 16, 21, 65. (NFC-e 65 também.)
- "Formato inválido — Modelo" ocorre quando série/modelo incorretos.

### Registro 70/71 (CT-e / transporte)
- Modelos aceitos: 7, 8, 9, 10, 11, 26, 57 (CT-e) e 58/67 conforme UF.
- CFOP de serviço de transporte exige conhecimento de transporte, não NF-e
  (modelo 55) — tema do corretor `corretor_cfop_transporte_registro50`.

### Registro 60 (ECF)
- Receita bruta do ECF (60M) = somatório dos analíticos (60A).
- 60D sem o 60M correspondente = erro; 60A em duplicidade = erro.
- Totalizadores de redução Z devem estar em maiúsculas.

### Registro 75
- Deve existir 75 para todo produto citado em 54/57/60D/60I/60R/74/77/86.
- NCM válido (8 posições), unidade de medida preenchida, alíquotas válidas.

### Registro 90 (totalização)
- Total por tipo (par tipo+total) deve conferir com a contagem real dos
  registros daquele tipo no arquivo.
- Total geral (últimos 8 dígitos) = total de linhas do arquivo
  (incluindo 10, 11 e o(s) próprio(s) 90).
- Tipos 10, 11 e 90 não têm par próprio no 90.
- "Encontrado final de arquivo antes do registro 90" = linha em branco ou
  falta do 90.

### Cancelamento de NF
- No SINTEGRA, cancelamento é indicado no campo 17 do 50 = "S".
- Para NF cancelada, o registro 54 é dispensável (mas aceitável se presente).

## Comportamentos frequentes (mensagens reais)

| Mensagem | Significado |
|----------|-------------|
| "CFOP inválido — Registro 50 — CFOP" | CFOP inexistente ou errado |
| "Formato inválido — Registro 10 — CNPJ" | CNPJ com DV errado |
| "Inscrição inválida para o UF" | IE com DV errado para a UF |
| "Não encontrado registro 50 correspondente" | 54 sem 50 (ou chave diferente) |
| "Dia deve ser 01" / "Dia deve ser 30 ou 31" | datas do 10 fora do padrão |
| "Data fora do período informado no registro 10" | doc fora do mês |
| "Conteúdo inexistente — CST" | CST em branco/inválido no 54 |
| "UF Inválida" | sigla de UF inexistente no 50 |
| "Modelo Inválido" | código de modelo não aceito |
| "Total de registros não confere" | par do 90 divergente |
| "Conteúdo inválido — Base de cálculo do ICMS" | valor inválido no 60 |
| "Alíquota inválida" | alíquota > 25% ou mal formatada |

## Como os corretores deste projeto se encaixam

- Detecção **por linha**: plugins que validam campos individuais
  (CNPJ, IE, UF, CFOP, CST, data, alíquota, modelo).
- Detecção **entre registros**: exige leitura do arquivo inteiro
  (50↔54, 60M↔60A, 90 totalizadores). O corretor de 90 usa estado interno
  no plugin; as demais podem ser adicionadas com hook de "final de arquivo".
