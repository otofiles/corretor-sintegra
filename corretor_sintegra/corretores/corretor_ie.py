from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from core.models import CorretorPlugin, ItemCorrecao, Registro

# ============================================================
# VALIDAÇÃO E CORREÇÃO DE INSCRIÇÕES ESTADUAIS (IE)
# ============================================================


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def weighted_sum(digits: str, weights: Sequence[int]) -> int:
    return sum(int(d) * w for d, w in zip(digits, weights))


def dv_mod11_11_minus_remainder(total: int) -> int:
    remainder = total % 11
    return 0 if remainder in (0, 1) else 11 - remainder


def dv_mod11_10_special(total: int) -> int:
    dv = 11 - (total % 11)
    return 0 if dv in (10, 11) else dv


@dataclass(frozen=True)
class ValidationResult:
    valida: bool
    uf: str
    ie: str
    formato: str = ""
    motivo: str = ""


@dataclass(frozen=True)
class Candidate:
    ie: str
    start: int
    end: int
    formato: str
    score: float = 0.0


@dataclass
class AnalysisResult:
    status: str
    original_line: str
    corrected_line: Optional[str] = None
    uf: str = ""
    ie_original: str = ""
    ie_corrigida: str = ""
    deslocamento: int = 0
    campos_afetados: str = ""
    motivo: str = ""
    regra: str = ""
    confianca: str = ""


def result_for_validation(
    uf: str, ie: str, formato: str, expected: int, calculated: int
) -> ValidationResult:
    return ValidationResult(
        valida=(calculated == expected),
        uf=uf,
        ie=ie,
        formato=formato,
        motivo="" if calculated == expected else f"DV calculado {calculated}, informado {expected}",
    )


# ---------- Regras das UFs ----------
def validar_ac(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 13 or not s.startswith("01"):
        return []
    base = s[:11]
    d1, d2 = int(s[11]), int(s[12])
    total1 = weighted_sum(base, [4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    c1 = dv_mod11_10_special(total1)
    total2 = weighted_sum(base + str(c1), [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    c2 = dv_mod11_10_special(total2)
    return [result_for_validation("AC", s, "AC-11+2", 10*d1+d2, 10*c1+c2)]


def validar_al(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9 or not s.startswith("24") or s[2] not in "03578":
        return []
    total = weighted_sum(s[:8], [9,8,7,6,5,4,3,2])
    calc = (total * 10) % 11
    if calc == 10:
        calc = 0
    return [result_for_validation("AL", s, "AL-8+1", int(s[8]), calc)]


def validar_ap(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9 or not s.startswith("03"):
        return []
    n = int(s[:8])
    if n < 3000001:
        return []
    if n <= 3017000:
        p, d = 5, 0
    elif n <= 3019022:
        p, d = 9, 1
    else:
        p, d = 0, 0
    total = p + weighted_sum(s[:8], [9,8,7,6,5,4,3,2])
    calc = 11 - (total % 11)
    if calc == 10:
        calc = 0
    elif calc == 11:
        calc = d
    return [result_for_validation("AP", s, "AP-03+6+1", int(s[8]), calc)]


def validar_am(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9:
        return []
    total = weighted_sum(s[:8], [9,8,7,6,5,4,3,2])
    if total < 11:
        calc = 11 - total
    else:
        calc = dv_mod11_11_minus_remainder(total)
    if calc > 9:
        return [ValidationResult(False, "AM", s, "AM-8+1",
                                 "A regra fornecida pode gerar 10 neste ramo; caso não definido no TXT.")]
    return [result_for_validation("AM", s, "AM-8+1", int(s[8]), calc)]


def validar_ba(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    out: List[ValidationResult] = []

    if len(s) == 8 and s[0] in "0123458":
        base = s[:6]
        total = weighted_sum(base, [7,6,5,4,3,2])
        r = total % 10
        d2 = 0 if r == 0 else 10-r
        total2 = weighted_sum(base + str(d2), [8,7,6,5,4,3,2])
        r2 = total2 % 10
        d1 = 0 if r2 == 0 else 10-r2
        out.append(result_for_validation("BA", s, "BA-6+2-M10", int(s[6:8]), d1*10+d2))

    if len(s) == 8 and s[0] in "679":
        base = s[:6]
        d2 = dv_mod11_11_minus_remainder(weighted_sum(base, [7,6,5,4,3,2]))
        d1 = dv_mod11_11_minus_remainder(weighted_sum(base + str(d2), [8,7,6,5,4,3,2]))
        out.append(result_for_validation("BA", s, "BA-6+2-M11", int(s[6:8]), d1*10+d2))

    if len(s) == 9 and s[1] in "0123458":
        base = s[:7]
        total = weighted_sum(base, [8,7,6,5,4,3,2])
        r = total % 10
        d2 = 0 if r == 0 else 10-r
        total2 = weighted_sum(base + str(d2), [9,8,7,6,5,4,3,2])
        r2 = total2 % 10
        d1 = 0 if r2 == 0 else 10-r2
        out.append(result_for_validation("BA", s, "BA-7+2-M10", int(s[7:9]), d1*10+d2))

    if len(s) == 9 and s[1] in "679":
        base = s[:7]
        d2 = dv_mod11_11_minus_remainder(weighted_sum(base, [8,7,6,5,4,3,2]))
        d1 = dv_mod11_11_minus_remainder(weighted_sum(base + str(d2), [9,8,7,6,5,4,3,2]))
        out.append(result_for_validation("BA", s, "BA-7+2-M11", int(s[7:9]), d1*10+d2))

    return out


def validar_ce(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9:
        return []
    calc = dv_mod11_10_special(weighted_sum(s[:8], [9,8,7,6,5,4,3,2]))
    return [result_for_validation("CE", s, "CE-8+1", int(s[8]), calc)]


def validar_df(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 13 or not s.startswith("07"):
        return []
    base = s[:11]
    d1, d2 = int(s[11]), int(s[12])

    w1 = list(reversed([2,3,4,5,6,7,8,9,2,3,4]))
    total1 = weighted_sum(base, w1)
    c1 = dv_mod11_10_special(total1)

    base2 = base + str(c1)
    w2 = list(reversed([2,3,4,5,6,7,8,9,2,3,4,5]))
    total2 = weighted_sum(base2, w2)
    c2 = dv_mod11_10_special(total2)

    return [result_for_validation("DF", s, "DF-11+2", d1*10+d2, c1*10+c2)]


def validar_es(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9:
        return []
    calc = dv_mod11_11_minus_remainder(weighted_sum(s[:8], [9,8,7,6,5,4,3,2]))
    return [result_for_validation("ES", s, "ES-8+1", int(s[8]), calc)]


def validar_go(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9:
        return []
    if not (s[:2] in {"10","11"} or s[:2] in {str(i) for i in range(20,30)}):
        return []
    calc = dv_mod11_11_minus_remainder(weighted_sum(s[:8], [9,8,7,6,5,4,3,2]))
    return [result_for_validation("GO", s, "GO-8+1", int(s[8]), calc)]


def validar_ma(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9 or not s.startswith("12"):
        return []
    calc = dv_mod11_11_minus_remainder(weighted_sum(s[:8], [9,8,7,6,5,4,3,2]))
    return [result_for_validation("MA", s, "MA-8+1", int(s[8]), calc)]


def validar_mt(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 11:
        return []
    calc = dv_mod11_11_minus_remainder(weighted_sum(s[:10], [3,2,9,8,7,6,5,4,3,2]))
    return [result_for_validation("MT", s, "MT-10+1", int(s[10]), calc)]


def validar_ms(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9 or s[:2] not in {"28","50"}:
        return []
    total = weighted_sum(s[:8], [9,8,7,6,5,4,3,2])
    r = total % 11
    if r == 0:
        calc = 0
    else:
        t = 11-r
        calc = 0 if t > 9 else t
    return [result_for_validation("MS", s, "MS-8+1", int(s[8]), calc)]


def validar_mg(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 13:
        return []

    base11 = s[:11]
    work = base11[:3] + "0" + base11[3:]
    products = [int(d) * (1 if i % 2 == 0 else 2) for i, d in enumerate(work)]
    digit_sum = sum(int(ch) for p in products for ch in str(p))
    d1 = (10 - (digit_sum % 10)) % 10

    base12 = base11 + str(d1)
    weights2 = [3,2,11,10,9,8,7,6,5,4,3,2]
    total2 = weighted_sum(base12, weights2)
    r2 = total2 % 11
    d2 = 0 if r2 in (0,1) else 11-r2

    return [result_for_validation("MG", s, "MG-11+2", int(s[11:13]), d1*10+d2)]


def validar_pa(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9 or s[:2] not in {"15","75","76","77","78","79"}:
        return []
    calc = dv_mod11_11_minus_remainder(weighted_sum(s[:8], [9,8,7,6,5,4,3,2]))
    return [result_for_validation("PA", s, "PA-8+1", int(s[8]), calc)]


def validar_pb(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9:
        return []
    calc = dv_mod11_10_special(weighted_sum(s[:8], [9,8,7,6,5,4,3,2]))
    return [result_for_validation("PB", s, "PB-8+1", int(s[8]), calc)]


def validar_pr(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 10:
        return []
    base8 = s[:8]
    d1 = dv_mod11_11_minus_remainder(weighted_sum(base8, [3,2,7,6,5,4,3,2]))
    base9 = base8 + str(d1)
    d2 = dv_mod11_11_minus_remainder(weighted_sum(base9, [4,3,2,7,6,5,4,3,2]))
    return [result_for_validation("PR", s, "PR-8+2", int(s[8:]), d1*10+d2)]


def validar_pe(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    out: List[ValidationResult] = []

    if len(s) == 9:
        base7 = s[:7]
        d1 = dv_mod11_11_minus_remainder(weighted_sum(base7, [8,7,6,5,4,3,2]))
        base8 = base7 + str(d1)
        d2 = dv_mod11_11_minus_remainder(weighted_sum(base8, [9,8,7,6,5,4,3,2]))
        out.append(result_for_validation("PE", s, "PE-eFisco-7+2", int(s[7:]), d1*10+d2))

    if len(s) == 14:
        base = s[:13]
        total = weighted_sum(base, [5,4,3,2,1,9,8,7,6,5,4,3,2])
        dv = 11 - (total % 11)
        if dv > 9:
            dv -= 10
        out.append(result_for_validation("PE", s, "PE-CACEPE-antiga-13+1", int(s[13]), dv))

    return out


def validar_pi(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9:
        return []
    calc = dv_mod11_10_special(weighted_sum(s[:8], [9,8,7,6,5,4,3,2]))
    return [result_for_validation("PI", s, "PI-8+1", int(s[8]), calc)]


def validar_rj(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 8:
        return []
    calc = dv_mod11_11_minus_remainder(weighted_sum(s[:7], [2,7,6,5,4,3,2]))
    return [result_for_validation("RJ", s, "RJ-7+1", int(s[7]), calc)]


def validar_rn(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    out: List[ValidationResult] = []

    if len(s) == 9 and s.startswith("20"):
        total = weighted_sum(s[:8], [9,8,7,6,5,4,3,2])
        calc = (total * 10) % 11
        if calc == 10:
            calc = 0
        out.append(result_for_validation("RN", s, "RN-8+1", int(s[8]), calc))

    if len(s) == 10 and s.startswith("20"):
        total = weighted_sum(s[:9], [10,9,8,7,6,5,4,3,2])
        calc = (total * 10) % 11
        if calc == 10:
            calc = 0
        out.append(result_for_validation("RN", s, "RN-9+1", int(s[9]), calc))

    return out


def validar_rs(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 10:
        return []
    calc = dv_mod11_10_special(weighted_sum(s[:9], [2,9,8,7,6,5,4,3,2]))
    return [result_for_validation("RS", s, "RS-9+1", int(s[9]), calc)]


def validar_ro(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    out: List[ValidationResult] = []

    if len(s) == 9:
        base5 = s[3:8]
        total = weighted_sum(base5, [6,5,4,3,2])
        dv = 11 - (total % 11)
        if dv in (10,11):
            dv -= 10
        out.append(result_for_validation("RO", s, "RO-antiga-3+5+1", int(s[8]), dv))

    if len(s) == 14:
        total = weighted_sum(s[:13], [6,5,4,3,2,9,8,7,6,5,4,3,2])
        dv = 11 - (total % 11)
        if dv in (10,11):
            dv -= 10
        out.append(result_for_validation("RO", s, "RO-nova-13+1", int(s[13]), dv))

    return out


def validar_rr(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9 or not s.startswith("24"):
        return []

    out = []

    total9 = sum((i+1) * int(d) for i, d in enumerate(s[:8]))
    calc9 = total9 % 9
    out.append(result_for_validation("RR", s, "RR-mod9", int(s[8]), calc9))

    total11 = weighted_sum(s[:8], [9,8,7,6,5,4,3,2])
    calc11 = dv_mod11_11_minus_remainder(total11)
    out.append(result_for_validation("RR", s, "RR-mod11", int(s[8]), calc11))

    return out


def validar_sc(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9:
        return []
    calc = dv_mod11_11_minus_remainder(weighted_sum(s[:8], [9,8,7,6,5,4,3,2]))
    return [result_for_validation("SC", s, "SC-8+1", int(s[8]), calc)]


def validar_sp(ie: str) -> List[ValidationResult]:
    raw = ie.upper().strip()
    s = re.sub(r"[^P0-9]", "", raw)
    out: List[ValidationResult] = []

    if len(s) == 12 and s.isdigit():
        total1 = sum(int(s[i]) * w for i, w in enumerate([1,3,4,5,6,7,8,10]))
        d1 = (total1 % 11) % 10

        total2 = sum(int(s[i]) * w for i, w in enumerate([3,2,10,9,8,7,6,5,4,3,2]))
        d2 = (total2 % 11) % 10

        informado = int(s[8]) * 10 + int(s[11])
        calculado = d1 * 10 + d2
        out.append(result_for_validation("SP", s, "SP-industrial-12", informado, calculado))

    if len(s) == 13 and s.startswith("P") and s[1:].isdigit():
        base = s[1:9]
        total = weighted_sum(base, [1,3,4,5,6,7,8,10])
        calc = (total % 11) % 10
        out.append(result_for_validation(
            "SP", s, "SP-produtor-P0MMMSSSSD000", int(s[9]), calc
        ))

    return out


def validar_se(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 9:
        return []
    calc = dv_mod11_10_special(weighted_sum(s[:8], [9,8,7,6,5,4,3,2]))
    return [result_for_validation("SE", s, "SE-8+1", int(s[8]), calc)]


def validar_to(ie: str) -> List[ValidationResult]:
    s = only_digits(ie)
    if len(s) != 11:
        return []

    if s[2:4] not in {"01","02","03","99"}:
        return []

    selected = "".join(s[:10][i] for i in (0,1,4,5,6,7,8,9))
    total = weighted_sum(selected, [9,8,7,6,5,4,3,2])
    r = total % 11
    calc = 0 if r < 2 else 11-r
    return [result_for_validation("TO", s, "TO-10+1", int(s[10]), calc)]


VALIDADORES: Dict[str, Callable[[str], List[ValidationResult]]] = {
    "AC": validar_ac, "AL": validar_al, "AP": validar_ap, "AM": validar_am,
    "BA": validar_ba, "CE": validar_ce, "DF": validar_df, "ES": validar_es,
    "GO": validar_go, "MA": validar_ma, "MT": validar_mt, "MS": validar_ms,
    "MG": validar_mg, "PA": validar_pa, "PB": validar_pb, "PR": validar_pr,
    "PE": validar_pe, "PI": validar_pi, "RJ": validar_rj, "RN": validar_rn,
    "RS": validar_rs, "RO": validar_ro, "RR": validar_rr, "SC": validar_sc,
    "SP": validar_sp, "SE": validar_se, "TO": validar_to,
}

REGRAS_UF = VALIDADORES


def validar_ie(uf: str, ie: str) -> Dict[str, object]:
    uf = uf.upper()
    validator = VALIDADORES.get(uf)

    if not validator:
        return {
            "valida": False,
            "uf": uf,
            "ie": ie,
            "formato": "",
            "motivo": "UF sem regra implementada.",
        }

    resultados = validator(ie)
    validos = [r for r in resultados if r.valida]

    if len(validos) == 1:
        r = validos[0]
        return {
            "valida": True,
            "uf": r.uf,
            "ie": r.ie,
            "formato": r.formato,
            "motivo": r.motivo,
        }

    if len(validos) > 1:
        return {
            "valida": True,
            "uf": uf,
            "ie": only_digits(ie),
            "formato": "|".join(r.formato for r in validos),
            "motivo": "Mais de um formato/regra do TXT valida a mesma IE.",
            "ambiguo": True,
        }

    return {
        "valida": False,
        "uf": uf,
        "ie": only_digits(ie),
        "formato": "|".join(r.formato for r in resultados),
        "motivo": "; ".join(r.motivo for r in resultados if r.motivo),
    }


def formatos_esperados(uf: str) -> List[int]:
    return {
        "AC": [13], "AL": [9], "AP": [9], "AM": [9], "BA": [8,9],
        "CE": [9], "DF": [13], "ES": [9], "GO": [9], "MA": [9],
        "MT": [11], "MS": [9], "MG": [13], "PA": [9], "PB": [9],
        "PR": [10], "PE": [9,14], "PI": [9], "RJ": [8], "RN": [9,10],
        "RS": [10], "RO": [9,14], "RR": [9], "SC": [9], "SP": [12,13],
        "SE": [9], "TO": [11],
    }.get(uf.upper(), [])


# ============================================================
# ÂNCORAS E CORREÇÃO
# ============================================================

UF_SET = set(VALIDADORES)
DATE_UF_RE = re.compile(r"(20\d{6})([A-Z]{2})(\d{2,3})")


@dataclass(frozen=True)
class Anchor:
    start: int
    date: str
    uf: str
    tail: str


def encontrar_ancoras_registro50(line: str) -> List[Anchor]:
    anchors: List[Anchor] = []
    for m in DATE_UF_RE.finditer(line):
        uf = m.group(2)
        if uf in UF_SET:
            anchors.append(Anchor(m.start(), m.group(1), uf, m.group(3)))
    return anchors


def cnpj_range(line: str) -> Optional[Tuple[int, int]]:
    if not line.startswith("50") or len(line) < 16:
        return None
    start = 2
    end = 16
    if not line[start:end].isdigit():
        return None
    return start, end


def ie_region(line: str, anchor: Anchor) -> Optional[Tuple[int, int]]:
    cr = cnpj_range(line)
    if not cr:
        return None
    start = cr[1]
    end = anchor.start
    if end <= start:
        return None
    return start, end


def extrair_candidatos_region(
    line: str,
    uf: str,
    region_start: int,
    region_end: int,
    max_edit: int = 3,
) -> List[Candidate]:
    region = line[region_start:region_end]
    expected_sizes = formatos_esperados(uf)
    candidates: Dict[Tuple[str,int,int,str], Candidate] = {}

    blocks = list(re.finditer(r"\d+", region))

    for block in blocks:
        text = block.group()
        abs_start = region_start + block.start()
        abs_end = region_start + block.end()

        if len(text) in expected_sizes:
            result = validar_ie(uf, text)
            if result.get("valida") and not result.get("ambiguo"):
                fmt = str(result.get("formato", ""))
                candidates[(text, abs_start, abs_end, fmt)] = Candidate(
                    text, abs_start, abs_end, fmt, 3.0
                )

        for size in expected_sizes:
            if len(text) >= size:
                for i in range(len(text) - size + 1):
                    sub = text[i:i+size]
                    result = validar_ie(uf, sub)
                    if result.get("valida") and not result.get("ambiguo"):
                        fmt = str(result.get("formato", ""))
                        candidates[(sub, abs_start+i, abs_start+i+size, fmt)] = Candidate(
                            sub, abs_start+i, abs_start+i+size, fmt, 2.0
                        )

        for size in expected_sizes:
            if len(text) > size and len(text)-size <= max_edit:
                for remove_idx in itertools.combinations(range(len(text)), len(text)-size):
                    sub = "".join(ch for i, ch in enumerate(text) if i not in remove_idx)
                    result = validar_ie(uf, sub)
                    if result.get("valida") and not result.get("ambiguo"):
                        fmt = str(result.get("formato", ""))
                        candidates[(sub, abs_start, abs_end, fmt)] = Candidate(
                            sub, abs_start, abs_end, fmt, 1.5
                        )

        for size in expected_sizes:
            for sub_len in range(1, len(text)+1):
                for i in range(len(text) - sub_len + 1):
                    sub = text[i:i+sub_len]
                    if len(sub) < size and size - len(sub) <= max_edit:
                        missing = size - len(sub)
                        for left in range(missing + 1):
                            right = missing - left
                            padded = ("0" * left) + sub + ("0" * right)
                            result = validar_ie(uf, padded)
                            if result.get("valida") and not result.get("ambiguo"):
                                fmt = str(result.get("formato", ""))
                                candidates[(padded, abs_start+i, abs_start+i+sub_len, fmt)] = Candidate(
                                    padded, abs_start+i, abs_start+i+sub_len, fmt, 2.5
                                )
                    if len(sub) < size and size - len(sub) <= max_edit:
                        padded = sub.zfill(size)
                        result = validar_ie(uf, padded)
                        if result.get("valida") and not result.get("ambiguo"):
                            fmt = str(result.get("formato", ""))
                            candidates[(padded, abs_start+i, abs_start+i+sub_len, fmt)] = Candidate(
                                padded, abs_start+i, abs_start+i+sub_len, fmt, 2.8
                            )

        for size in expected_sizes:
            if len(text) < size and size - len(text) <= max_edit:
                missing = size - len(text)
                for left in range(missing + 1):
                    right = missing - left
                    padded = ("0" * left) + text + ("0" * right)
                    result = validar_ie(uf, padded)
                    if result.get("valida") and not result.get("ambiguo"):
                        fmt = str(result.get("formato", ""))
                        candidates[(padded, abs_start, abs_end, fmt)] = Candidate(
                            padded, abs_start, abs_end, fmt, 3.0
                        )

    compact = "".join(ch for ch in region if ch.isdigit())
    if compact:
        for size in expected_sizes:
            if len(compact) >= size:
                for i in range(len(compact)-size+1):
                    sub = compact[i:i+size]
                    result = validar_ie(uf, sub)
                    if result.get("valida") and not result.get("ambiguo"):
                        fmt = str(result.get("formato", ""))
                        candidates[(sub, region_start, region_end, fmt)] = Candidate(
                            sub, region_start, region_end, fmt, 0.5
                        )
            for sub_len in range(1, len(compact)+1):
                for i in range(len(compact)-sub_len+1):
                    sub = compact[i:i+sub_len]
                    if len(sub) < size and size - len(sub) <= max_edit:
                        padded = sub.zfill(size)
                        result = validar_ie(uf, padded)
                        if result.get("valida") and not result.get("ambiguo"):
                            fmt = str(result.get("formato", ""))
                            candidates[(padded, region_start, region_end, fmt)] = Candidate(
                                padded, region_start, region_end, fmt, 0.8
                            )

    return list(candidates.values())


def avaliar_consistencia(line: str, anchor: Anchor, candidate: Candidate) -> float:
    region = ie_region(line, anchor)
    if not region:
        return -999.0

    region_start, region_end = region
    score = candidate.score

    if candidate.start == region_start:
        score += 2.0
    if candidate.end == region_end:
        score += 1.0
    if candidate.ie.isdigit():
        score += 0.5

    return score


def reconstruir_linha(
    line: str,
    anchor: Anchor,
    candidate: Candidate,
    region_start: int,
    region_end: int,
) -> str:
    region = line[region_start:region_end]
    before = line[:region_start]
    suffix = line[anchor.start:]

    original_digits = "".join(ch for ch in region if ch.isdigit())

    pos = region.find(original_digits)
    if pos == -1:
        new_region = candidate.ie + ' ' * (len(region) - len(candidate.ie))
        if len(new_region) < len(region):
            new_region += ' ' * (len(region) - len(new_region))
        elif len(new_region) > len(region):
            new_region = new_region[:len(region)]
        return before + new_region + suffix

    left_spaces = region[:pos]
    right_spaces = region[pos + len(original_digits):]
    new_region = left_spaces + candidate.ie + right_spaces

    if len(new_region) != len(region):
        diff = len(region) - len(new_region)
        if diff > 0:
            new_region += ' ' * diff
        elif diff < 0:
            new_region = new_region[:len(region)]

    return before + new_region + suffix


class CorretorIE:
    def __init__(self, modo_simulacao: bool = False):
        self.modo_simulacao = modo_simulacao

    def analisar_linha(self, line: str) -> AnalysisResult:
        original = line

        if not line.startswith("50"):
            return AnalysisResult(
                "NAO_CORRIGIDA", original,
                motivo="Registro diferente de 50."
            )

        anchors = encontrar_ancoras_registro50(line)
        if not anchors:
            return AnalysisResult(
                "NAO_CORRIGIDA", original,
                motivo="Não foi encontrada âncora data+UF."
            )

        solutions = []

        for anchor in anchors:
            region = ie_region(line, anchor)
            if not region:
                continue

            rs, re_ = region
            compact = "".join(ch for ch in line[rs:re_] if ch.isdigit())
            current = validar_ie(anchor.uf, compact)

            if current.get("valida") and not current.get("ambiguo"):
                continue

            candidates = extrair_candidatos_region(
                line, anchor.uf, rs, re_
            )

            for c in candidates:
                score = avaliar_consistencia(line, anchor, c)
                solutions.append((score, anchor, c, rs, re_))

        if not solutions:
            return AnalysisResult(
                "NAO_CORRIGIDA",
                original,
                motivo="Nenhuma IE candidata válida foi encontrada segundo a regra da UF.",
            )

        solutions.sort(key=lambda x: x[0], reverse=True)
        best_score = solutions[0][0]
        best = [s for s in solutions if abs(s[0]-best_score) < 1e-9]

        unique_ie = {
            (s[2].ie, s[1].start, s[2].formato)
            for s in best
        }

        if len(unique_ie) > 1:
            return AnalysisResult(
                "AMBIGUA",
                original,
                uf=best[0][1].uf,
                ie_original="".join(
                    ch for ch in line[best[0][3]:best[0][4]]
                    if ch.isdigit()
                ),
                motivo="Mais de uma solução igualmente consistente.",
                regra="; ".join(sorted({s[2].formato for s in best})),
                confianca="BAIXA",
            )

        score, anchor, candidate, rs, re_ = best[0]
        original_ie = "".join(
            ch for ch in line[rs:re_] if ch.isdigit()
        )

        corrected = reconstruir_linha(
            line, anchor, candidate, rs, re_
        )

        status = "SIMULACAO" if self.modo_simulacao else "CORRIGIDA"

        if corrected == original:
            return AnalysisResult(
                "NAO_CORRIGIDA",
                original,
                uf=anchor.uf,
                ie_original=original_ie,
                ie_corrigida=candidate.ie,
                motivo="Candidato válido, mas a reconstrução não alterou a linha.",
                regra=candidate.formato,
                confianca="ALTA",
            )

        delta = len(candidate.ie) - len(original_ie)

        return AnalysisResult(
            status,
            original,
            corrected_line=corrected,
            uf=anchor.uf,
            ie_original=original_ie,
            ie_corrigida=candidate.ie,
            deslocamento=delta,
            campos_afetados="IE e separador adjacente à IE",
            motivo="IE candidata validada pela regra oficial da UF e única solução encontrada.",
            regra=candidate.formato,
            confianca="ALTA" if score >= 4.0 else "MEDIA",
        )


_CORRETOR = CorretorIE(modo_simulacao=False)


def _regiao_ie_isenta(linha: str) -> bool:
    for ancora in encontrar_ancoras_registro50(linha):
        regiao = ie_region(linha, ancora)
        if regiao:
            ini, fim = regiao
            if "ISENTO" in linha[ini:fim].upper():
                return True
    return False


_IE_NOTAS_RELATADAS: set = set()


def _nota_registro50(linha: str) -> Optional[str]:
    if len(linha) >= 51:
        return linha[45:51]
    return None


def _emitir_apontamento_ie(
    registro: Registro, linha: str, motivo: str, regra: str, confianca: str
) -> List[ItemCorrecao]:
    nota = _nota_registro50(linha)
    if nota and nota in _IE_NOTAS_RELATADAS:
        return []
    if nota:
        _IE_NOTAS_RELATADAS.add(nota)
    if nota:
        descricao = (
            f"Nota fiscal {nota}: Inscrição Estadual (IE) precisa de correção. "
            "Confira a IE informada nessa nota no seu sistema e corrija se estiver errada."
        )
    else:
        descricao = motivo or "Inscrição Estadual (IE) precisa de correção."
    return [
        ItemCorrecao(
            numero_linha=registro.numero_linha,
            tipo_registro=registro.tipo,
            texto_original=linha,
            confianca=confianca,
            descricao=descricao,
            regra=regra,
            corrigir=False,
        )
    ]


def _analisar(registro: Registro) -> List[ItemCorrecao]:
    linha = registro.conteudo
    if registro.tipo == "10":
        _IE_NOTAS_RELATADAS.clear()
        return []
    if not linha.startswith("50"):
        return []

    if _regiao_ie_isenta(linha):
        return []

    for ancora in encontrar_ancoras_registro50(linha):
        regiao = ie_region(linha, ancora)
        if regiao:
            ini, fim = regiao
            compacto = "".join(ch for ch in linha[ini:fim] if ch.isdigit())
            validacao = validar_ie(ancora.uf, compacto)
            if validacao.get("valida") and not validacao.get("ambiguo"):
                return []

    resultado = _CORRETOR.analisar_linha(linha)

    if resultado.status == "AMBIGUA":
        return _emitir_apontamento_ie(
            registro, linha,
            resultado.motivo or "Mais de uma solução igualmente consistente.",
            resultado.regra, "BAIXA",
        )

    if resultado.status in ("CORRIGIDA", "SIMULACAO"):
        return [
            ItemCorrecao(
                numero_linha=registro.numero_linha,
                tipo_registro=registro.tipo,
                texto_original=linha,
                texto_corrigido=resultado.corrected_line,
                confianca=resultado.confianca or "MEDIA",
                descricao=resultado.motivo or "IE inválida corrigida.",
                regra=resultado.regra,
                corrigir=True,
            )
        ]

    motivo = resultado.motivo or ""
    if "âncora" in motivo or "reconstrução não alterou" in motivo or "Registro diferente de 50" in motivo:
        return []
    return _emitir_apontamento_ie(
        registro, linha, motivo or "Registro não corrigido.", resultado.regra, "BAIXA"
    )


plugin = CorretorPlugin(
    id="corretor_ie",
    nome="Corretor de Inscrição Estadual (IE)",
    descricao="Valida e corrige Inscrições Estaduais nos registros 50 conforme a regra de cada UF. IE marcada como ISENTO é considerada válida.",
    versao="1.1",
    registros_afetados=["50", "10"],
    analisar=_analisar,
)
