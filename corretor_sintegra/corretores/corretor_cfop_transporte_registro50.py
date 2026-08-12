from __future__ import annotations

from typing import List, Optional, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro

MODELOS_TRANSPORTE = {
    "07": "Nota Fiscal de Serviço de Transporte",
    "08": "Conhecimento de Transporte Rodoviário de Cargas (CTRC)",
    "09": "Conhecimento de Transporte Aquaviário de Cargas",
    "10": "Conhecimento de Transporte Aéreo",
    "11": "Conhecimento de Transporte Ferroviário de Cargas",
    "26": "Conhecimento de Transporte Multimodal de Cargas",
    "57": "Conhecimento de Transporte Eletrônico (CT-e)",
    "67": "CT-e de Outros Serviços (CT-e OS)",
}

CFOP_TRANSPORTE = {
    "1206", "1351", "1352", "1353", "1354", "1355", "1356", "1360",
    "1931", "1932", "2206", "2351", "2352", "2353", "2354", "2355",
    "2356", "2931", "2932", "3206", "3351", "3352", "3353", "3354",
    "3355", "3356", "5206", "5351", "5352", "5353", "5354", "5355",
    "5356", "5357", "5359", "5360", "5931", "5932", "6206", "6351",
    "6352", "6353", "6354", "6355", "6356", "6357", "6359", "6931",
    "6932", "7358",
}

CFOP_DESCRICAO = {
    "1206": "Anulação de valor relativo à prestação de serviço de transporte",
    "1351": "Aquisição de serviço de transporte para execução de serviço da mesma natureza",
    "1352": "Aquisição de serviço de transporte por estabelecimento industrial",
    "1353": "Aquisição de serviço de transporte por estabelecimento comercial",
    "1354": "Aquisição de serviço de transporte por estabelecimento de prestador de serviço de comunicação",
    "1355": "Aquisição de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica",
    "1356": "Aquisição de serviço de transporte por estabelecimento de produtor rural",
    "1360": "Aquisição de serviço de transporte por contribuinte substituto em relação ao serviço de transporte",
    "1931": "Lançamento efetuado pelo tomador do serviço de transporte quando a responsabilidade de retenção do imposto for atribuída ao remetente ou alienante da mercadoria",
    "1932": "Aquisição de serviço de transporte iniciado em unidade da Federação diversa daquela onde inscrito o prestador",
    "2206": "Anulação de valor relativo à prestação de serviço de transporte",
    "2351": "Aquisição de serviço de transporte para execução de serviço da mesma natureza",
    "2352": "Aquisição de serviço de transporte por estabelecimento industrial",
    "2353": "Aquisição de serviço de transporte por estabelecimento comercial",
    "2354": "Aquisição de serviço de transporte por estabelecimento de prestador de serviço de comunicação",
    "2355": "Aquisição de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica",
    "2356": "Aquisição de serviço de transporte por estabelecimento de produtor rural",
    "2931": "Lançamento efetuado pelo tomador do serviço de transporte quando a responsabilidade de retenção do imposto for atribuída ao remetente ou alienante da mercadoria",
    "2932": "Aquisição de serviço de transporte iniciado em unidade da Federação diversa daquela onde inscrito o prestador",
    "3206": "Anulação de valor relativo à prestação de serviço de transporte",
    "3351": "Aquisição de serviço de transporte para execução de serviço da mesma natureza",
    "3352": "Aquisição de serviço de transporte por estabelecimento industrial",
    "3353": "Aquisição de serviço de transporte por estabelecimento comercial",
    "3354": "Aquisição de serviço de transporte por estabelecimento de prestador de serviço de comunicação",
    "3355": "Aquisição de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica",
    "3356": "Aquisição de serviço de transporte por estabelecimento de produtor rural",
    "5206": "Anulação de valor relativo à prestação de serviço de transporte",
    "5351": "Prestação de serviço de transporte para execução de serviço da mesma natureza",
    "5352": "Prestação de serviço de transporte por estabelecimento industrial",
    "5353": "Prestação de serviço de transporte por estabelecimento comercial",
    "5354": "Prestação de serviço de transporte por estabelecimento de prestador de serviço de comunicação",
    "5355": "Prestação de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica",
    "5356": "Prestação de serviço de transporte por estabelecimento de produtor rural",
    "5357": "Prestação de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica em substituição tributária",
    "5359": "Prestação de serviço de transporte por contribuinte substituto (CST 090)",
    "5360": "Prestação de serviço de transporte por contribuinte substituto (CST 010)",
    "5931": "Lançamento efetuado pelo tomador do serviço de transporte quando a responsabilidade de retenção do imposto for atribuída ao remetente ou alienante da mercadoria",
    "5932": "Prestação de serviço de transporte iniciado em unidade da Federação diversa daquela onde inscrito o prestador",
    "6206": "Anulação de valor relativo à prestação de serviço de transporte",
    "6351": "Prestação de serviço de transporte para execução de serviço da mesma natureza",
    "6352": "Prestação de serviço de transporte por estabelecimento industrial",
    "6353": "Prestação de serviço de transporte por estabelecimento comercial",
    "6354": "Prestação de serviço de transporte por estabelecimento de prestador de serviço de comunicação",
    "6355": "Prestação de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica",
    "6356": "Prestação de serviço de transporte por estabelecimento de produtor rural",
    "6357": "Prestação de serviço de transporte por estabelecimento de geradora ou de distribuidora de energia elétrica em substituição tributária",
    "6359": "Prestação de serviço de transporte por contribuinte substituto (CST 090)",
    "6931": "Lançamento efetuado pelo tomador do serviço de transporte quando a responsabilidade de retenção do imposto for atribuída ao remetente ou alienante da mercadoria",
    "6932": "Prestação de serviço de transporte iniciado em unidade da Federação diversa daquela onde inscrito o prestador",
    "7358": "Prestação de serviço de transporte na execução de exportação (fretes internacionais)",
}


def _extrair_modelo_cfop(registro: Registro) -> Optional[Tuple[str, str, str]]:
    linha = registro.conteudo
    if len(linha) < 55:
        return None
    modelo = linha[40:42]
    numero = linha[45:51]
    cfop = linha[51:55]
    if numero.isdigit() and cfop.isdigit() and cfop in CFOP_TRANSPORTE:
        return modelo, numero, cfop
    return None


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    if registro.tipo != "50":
        return []
    extraido = _extrair_modelo_cfop(registro)
    if extraido is None:
        return []
    modelo, numero, cfop = extraido

    if modelo in MODELOS_TRANSPORTE:
        return []

    descricao_cfop = CFOP_DESCRICAO.get(cfop, "transporte")
    numero_limpo = numero.lstrip("0") or "0"
    sugestao = (
        f"Número {numero_limpo} (reg. {registro.tipo}): CFOP {cfop} "
        f"({descricao_cfop}) é de serviço de transporte, mas o registro usa "
        f"modelo {modelo}, que não é de conhecimento de transporte. "
        f"Reimporte este documento como CT-e (modelo 57) ou CT-e OS "
        f"(modelo 67). Modelos de CT válidos no SINTEGRA: 07, 08, 09, 10, "
        f"11, 26, 57, 67."
    )
    return [
        ItemCorrecao(
            numero_linha=registro.numero_linha,
            tipo_registro=registro.tipo,
            texto_original=registro.conteudo,
            confianca="ALTA",
            descricao=sugestao,
            regra=f"CFOP {cfop} exige modelo de transporte (57/67)",
            corrigir=False,
        )
    ]


plugin = CorretorPlugin(
    id="corretor_cfop_transporte_registro50",
    nome="Corretor de CFOP de Transporte (reg. 50)",
    descricao=(
        "Analisa registros 50 (total da NF) cujo CFOP é de serviço de "
        "transporte, mas foram importados com modelo incorreto (ex.: 55 = "
        "NF-e) em vez de CT-e."
    ),
    versao="2.0",
    registros_afetados=["50"],
    analisar=_analisar,
)
