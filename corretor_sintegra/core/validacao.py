from __future__ import annotations

import calendar
import datetime

UFS = {
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG",
    "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR",
    "RS", "SC", "SE", "SP", "TO", "EX",
}

TIPOS_REGISTRO = {
    "10", "11", "50", "51", "53", "54", "55", "56", "57", "60", "61",
    "70", "71", "74", "75", "76", "77", "85", "86", "88", "90",
}

MODELOS_VALIDOS = {
    "01", "1A", "02", "03", "04", "06", "07", "08", "09", "10", "11",
    "13", "14", "15", "16", "17", "20", "21", "22", "26", "27", "55",
    "57", "58", "59", "65", "67",
}


def apenas_digitos(texto: str) -> str:
    return "".join(c for c in texto if c.isdigit())


def dv_cnpj(base: str) -> str:
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    soma = sum(int(base[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    d1 = 0 if resto < 2 else 11 - resto
    soma2 = sum(int((base + str(d1))[i]) * pesos2[i] for i in range(13))
    resto2 = soma2 % 11
    d2 = 0 if resto2 < 2 else 11 - resto2
    return f"{d1}{d2}"


def validar_cnpj(cnpj: str) -> bool:
    if len(cnpj) != 14 or not cnpj.isdigit():
        return False
    if cnpj in ("0" * 14, "1" * 14, "2" * 14, "3" * 14, "4" * 14, "5" * 14,
                "6" * 14, "7" * 14, "8" * 14, "9" * 14):
        return False
    return dv_cnpj(cnpj[:12]) == cnpj[12:]


def dv_cpf(base: str) -> str:
    soma1 = sum(int(base[i]) * (10 - i) for i in range(9))
    d1 = 0 if soma1 % 11 < 2 else 11 - (soma1 % 11)
    soma2 = sum(int((base + str(d1))[i]) * (11 - i) for i in range(10))
    d2 = 0 if soma2 % 11 < 2 else 11 - (soma2 % 11)
    return f"{d1}{d2}"


def validar_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    if cpf in ("0" * 11, "1" * 11, "2" * 11, "3" * 11, "4" * 11, "5" * 11,
               "6" * 11, "7" * 11, "8" * 11, "9" * 11):
        return False
    return dv_cpf(cpf[:9]) == cpf[9:]


def eh_data_valida(data: str) -> bool:
    if len(data) != 8 or not data.isdigit():
        return False
    ano, mes, dia = int(data[:4]), int(data[4:6]), int(data[6:8])
    if not 1900 <= ano <= 2100:
        return False
    try:
        datetime.date(ano, mes, dia)
        return True
    except ValueError:
        return False


def ultimo_dia_do_mes(data: str) -> str:
    ano, mes = int(data[:4]), int(data[4:6])
    ultimo = calendar.monthrange(ano, mes)[1]
    return f"{ano:04d}{mes:02d}{ultimo:02d}"


def validar_cfop(cfop: str) -> bool:
    if len(cfop) != 4 or not cfop.isdigit():
        return False
    if cfop == "0000":
        return False
    return cfop[0] in "123567"
