import os, re
from typing import Dict, List, Tuple
from schemas import DocRecord, ExtractResult
from extract_text import extract_pdf_text
from rag import retrieve_knowledge, format_hits
from llm import is_enabled, llm_extract_json

MAX_DOC_CHARS = int(os.getenv("MAX_DOC_CHARS", "22000"))

CPF_RE = re.compile(r"\b(\d{3}\.?(\d{3})\.?(\d{3})\-?\d{2})\b")
MONEY_RE = re.compile(r"R\$\s*([\d\.]+,\d{2})")
DATE_RE = re.compile(r"\b(\d{2}[/\-]\d{2}[/\-]\d{4})\b")

PAID_HINTS = [
    "PAGO", "PAGAMENTO EFETUADO", "PAGAMENTO CONFIRMADO", "TRANSACAO EFETUADA",
    "COMPROVANTE", "AUTENTICACAO", "AUTENTICAÇÃO", "QUITADO", "LIQUIDADO"
]

PAYER_LABELS = ["PAGADOR", "CPF DO PAGADOR", "CPF PAGADOR", "DADOS DO PAGADOR"]
NON_PAYER_LABELS = ["BENEFICIARIO", "BENEFICIÁRIO", "CEDENTE", "EMITENTE", "FAVORECIDO", "RECEBEDOR"]

def _clean_upper(s: str) -> str:
    return " ".join(s.upper().split())

def _digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def find_payer_cpf(text: str) -> str | None:
    t = _clean_upper(text)
    matches = list(CPF_RE.finditer(t))
    if not matches:
        return None

    candidates = []
    for m in matches:
        cpf = m.group(1)
        pos = m.start()

        w0 = max(0, pos - 180)
        w1 = min(len(t), pos + 180)
        ctx = t[w0:w1]

        score = 0
        for lab in PAYER_LABELS:
            if lab in ctx:
                score += 8
        for lab in NON_PAYER_LABELS:
            if lab in ctx:
                score -= 10
        if "CPF" in ctx:
            score += 2
        if len(_digits(cpf)) == 11:
            score += 1

        candidates.append((score, cpf, pos))

    candidates.sort(key=lambda x: (x[0], -x[2]), reverse=True)
    best_score, best_cpf, _ = candidates[0]

    if best_score < 2:
        # conservative fallback: first CPF in text
        return matches[0].group(1)

    return best_cpf

def parse_money_br(s: str) -> float:
    s = s.replace(".", "").replace(",", ".")
    return float(s)

def normalize_date_br(d: str) -> str:
    d = d.replace("-", "/")
    dd, mm, yyyy = d.split("/")
    return f"{yyyy}-{mm}-{dd}"

def detect_payment_status(text: str) -> str:
    t = text.upper()
    if any(h in t for h in PAID_HINTS):
        return "paid"
    if "VENCIMENTO" in t or "VENCE" in t:
        return "unpaid"
    return "unknown"

def extract_fields_regex(text: str) -> Dict:
    cpf = find_payer_cpf(text)

    total_value = None
    vals = MONEY_RE.findall(text)
    if vals:
        nums = [parse_money_br(v) for v in vals]
        total_value = max(nums)

    payment_status = detect_payment_status(text)

    payment_date = None
    dm = DATE_RE.findall(text)
    if dm:
        try:
            payment_date = normalize_date_br(dm[0])
        except Exception:
            payment_date = None

    auth_code = None
    m2 = re.search(r"(AUTENTICACAO|AUTENTICAÇÃO|COD\.?\s*AUT)\s*[:\-]?\s*([A-Z0-9\-\/]{6,})", text, re.IGNORECASE)
    if m2:
        auth_code = m2.group(2)

    linha_digitavel = None
    m3 = re.search(r"(\d{5}\.?(\d{5})\s*\d{5}\.?(\d{6})\s*\d{5}\.?(\d{6})\s*\d\s*\d{14})", text)
    if m3:
        linha_digitavel = " ".join(m3.group(1).split())

    return {
        "cpf": cpf,
        "total_value": total_value,
        "payment_status": payment_status,
        "payment_date": payment_date,
        "auth_code": auth_code,
        "linha_digitavel": linha_digitavel,
    }

def validate_record(rec: DocRecord) -> List[str]:
    issues = []
    if not rec.cpf:
        issues.append("CPF do pagador não encontrado")
    else:
        if len(_digits(rec.cpf)) != 11:
            issues.append("CPF do pagador inválido (tamanho != 11)")
    if rec.payment_status == "paid" and rec.payment_date is None and rec.auth_code is None:
        issues.append("Pago, mas sem evidência forte (data/auth_code ausentes)")
    if rec.total_value is None:
        issues.append("Valor não encontrado")
    if rec.total_value is not None and rec.total_value <= 0:
        issues.append("Valor inválido (<= 0)")
    return issues

def build_extraction_prompt(pdf_text: str, knowledge_context: str) -> Tuple[str, str]:
    system = (
        "Você é um extrator de dados de comprovantes/boletos escaneados (OCR pode ter ruído).\n"
        "Retorne APENAS JSON válido.\n"
        "CPF alvo: CPF DO PAGADOR.\n"
        "Priorize o CPF que aparecer no bloco rotulado como 'PAGADOR' (ou 'CPF DO PAGADOR').\n"
        "Evite CPF/CNPJ do BENEFICIÁRIO/CEDENTE/EMITENTE.\n"
        "Se houver mais de um CPF, escolha o do PAGADOR. Se incerto, use null.\n"
        "Campos (JSON):\n"
        "{"
        "\"cpf\": string|null, "
        "\"payer_name\": string|null, "
        "\"beneficiary\": string|null, "
        "\"linha_digitavel\": string|null, "
        "\"barcode\": string|null, "
        "\"total_value\": number|null, "
        "\"payment_status\": \"paid\"|\"unpaid\"|\"unknown\"|null, "
        "\"payment_date\": string|null, "
        "\"auth_code\": string|null, "
        "\"notes\": string|null"
        "}\n"
        "Preferir payment_date em YYYY-MM-DD se possível."
    )

    user = (
        f"Contexto (SOPs / regras):\n{knowledge_context}\n\n"
        f"Texto OCR do documento:\n{pdf_text}"
    )
    return system, user

async def extract_with_llm(file_name: str, pdf_text: str, knowledge_context: str) -> DocRecord:
    system, user = build_extraction_prompt(pdf_text, knowledge_context)
    data = await llm_extract_json(system=system, user=user)

    rec = DocRecord(
        file_name=file_name,
        doc_type="boleto_comprovante",
        cpf=data.get("cpf"),
        payer_name=data.get("payer_name"),
        beneficiary=data.get("beneficiary"),
        linha_digitavel=data.get("linha_digitavel"),
        barcode=data.get("barcode"),
        total_value=data.get("total_value"),
        payment_status=data.get("payment_status") or "unknown",
        payment_date=data.get("payment_date"),
        auth_code=data.get("auth_code"),
        notes=data.get("notes"),
    )
    return rec

async def process_inbox(inbox_dir="inbox") -> List[ExtractResult]:
    out: List[ExtractResult] = []

    for fn in os.listdir(inbox_dir):
        if not fn.lower().endswith(".pdf"):
            continue

        path = os.path.join(inbox_dir, fn)
        text = extract_pdf_text(path)

        hits = retrieve_knowledge("Regras para extração de CPF do pagador e confirmação de pagamento de boleto", k=4)
        sources = [h["meta"]["source"] for h in hits]
        knowledge_context = format_hits(hits)

        clipped = (text or "")[:MAX_DOC_CHARS]

        rec = None
        issues: List[str] = []
        used_llm = False

        if is_enabled() and clipped.strip():
            try:
                rec = await extract_with_llm(fn, clipped, knowledge_context)
                used_llm = True
            except Exception as e:
                issues.append(f"LLM falhou, usando regex: {type(e).__name__}")

        if rec is None:
            fields = extract_fields_regex(text)
            rec = DocRecord(file_name=fn, doc_type="boleto_comprovante", **fields)

        issues.extend(validate_record(rec))
        issues.append("extração:llm" if used_llm else "extração:regex_fallback")

        out.append(ExtractResult(record=rec, issues=issues, knowledge_sources=sources))

    return out
