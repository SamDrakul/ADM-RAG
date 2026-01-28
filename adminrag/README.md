# AdminRAG  
OCR + RAG + Administrative Automation with Python

End-to-end pipeline for processing scanned PDF payment receipts and bank slips, extracting the payer’s CPF, confirming payment status, applying internal rules via RAG, and generating spreadsheets, reports, and audit logs.

---

## Overview

This project addresses a common real-world administrative problem:

“We receive many scanned payment receipts. How can we reliably extract data, validate internal rules, and generate reports without manual work?”

AdminRAG provides a production-oriented solution combining:
- OCR for scanned PDFs
- RAG (Retrieval-Augmented Generation) over internal SOPs
- Structured data extraction with deterministic fallback
- Secure automation with dry-run support
- Full execution audit trail

Built entirely in Python with a strong focus on reliability, security, and real business use cases.

---

## Key Features

### Input
- Scanned PDFs (payment receipts / bank slips)
- Internal rules and SOPs (plain text)

### Processing
1. Automatic OCR with image pre-processing  
2. Retrieval of internal rules using RAG  
3. Hybrid extraction:
   - LLM-based extraction (optional)
   - Regex + heuristic fallback
4. Payer CPF identification
5. Payment confirmation detection
6. Data validation
7. Safe planning and execution of automation steps

### Output
- Excel spreadsheet (.xlsx)
- Markdown report (.md)
- JSON audit log (.json)

---

## Security by design

- No secrets committed to the repository
- Environment-variable based configuration
- Isolated workspace for file generation
- Explicit tool allowlist
- Full audit trail per execution
- Dry-run mode for safe simulation

---

## Author

Developed as a technical portfolio project focused on Python, automation, and applied AI.
