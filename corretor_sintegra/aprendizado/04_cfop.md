# 04 - Catálogo de CFOP

O CFOP (Código Fiscal de Operações e Prestações) é definido pela tabela
nacional da CONFAZ (decreto que aprova a tabela de CFOP, ex.: Decreto nº
4.789/2003 e atualizações). Este projeto usa **validação estrutural**, que
não requer a tabela completa.

## Validação estrutural (segura, sem falso-positivo)

- Campo CFOP tem **4 posições**, sempre numéricas.
- Primeiro dígito indica o grupo:

| Dígito | Grupo | Direção |
|--------|-------|---------|
| 1 | Entradas — compras/aquisições | entrada |
| 2 | Entradas — devoluções de compras | entrada |
| 3 | Entradas — prestações de serviço | entrada |
| 5 | Saídas — vendas/produção | saída |
| 6 | Saídas — devoluções de vendas | saída |
| 7 | Saídas — prestações de serviço | saída |

- Dígitos 4, 8 e 9 no início: **inválidos** (não existem grupos 4/8/9).
- CFOP `0000`: inválido (código vazio).

## Subgrupos relevantes usados nos corretores

- `1351..1356`, `2351..2356`, `3351..3356` — serviço de transporte (entrada).
- `5351..5360`, `6351..6360`, `7358` — serviço de transporte (saída).
- `1206`, `2206`, `5206`, `6206` — anulação de serviço de transporte.
- `1931/1932`, `2931/2932`, `5931/5932`, `6931/6932` — retenção/ST de transporte.

A lista completa desses CFOPs de transporte está em
`corretores/corretor_cfop_transporte_registro50.py` (`CFOP_TRANSPORTE`).

## Limite desta abordagem

A validação estrutural NÃO detecta um CFOP inexistente mas com dígito inicial
válido (ex.: 5999). Para isso seria preciso a tabela completa da CONFAZ
(~1.000 códigos), que pode ser adicionada futuramente como
`corretores/dados/cfop.txt` e consultada pelo corretor de CFOP.
