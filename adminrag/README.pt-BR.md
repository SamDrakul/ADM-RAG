# AdminRAG  
OCR + RAG + Automação Administrativa com Python

Pipeline completo para processamento de PDFs escaneados de boletos e comprovantes de pagamento, com extração do CPF do PAGADOR, confirmação de pagamento, aplicação de regras internas (RAG) e geração automática de planilhas, relatórios e auditoria.

---

## Visão geral

Este projeto resolve um problema comum em rotinas administrativas e financeiras:

“Recebemos diversos comprovantes de pagamento escaneados. Como extrair dados confiáveis, validar regras internas e gerar relatórios sem trabalho manual?”

O AdminRAG implementa uma solução end-to-end combinando:
- OCR para PDFs escaneados
- RAG (Retrieval-Augmented Generation) para regras internas (SOPs)
- Extração estruturada com fallback determinístico
- Automação segura com dry-run
- Auditoria completa por execução

Tudo desenvolvido em Python, com foco em confiabilidade, segurança e uso real em ambientes corporativos.

---

## Funcionalidades principais

### Entrada
- PDFs escaneados (boletos e comprovantes)
- Arquivos de regras internas (SOPs em texto)

### Processamento
1. OCR automático com pré-processamento de imagem  
2. Consulta às regras internas via RAG  
3. Extração híbrida:
   - LLM (opcional)
   - Fallback com regex e heurísticas
4. Identificação do CPF do PAGADOR
5. Detecção de pagamento confirmado
6. Validação de dados
7. Planejamento e execução controlada de automações

### Saídas
- Planilha Excel (.xlsx)
- Relatório em Markdown (.md)
- Log de auditoria (.json)

---

## Segurança por design

- Nenhuma credencial sensível versionada
- Uso exclusivo de variáveis de ambiente
- Workspace isolado para escrita de arquivos
- Allowlist explícita de ferramentas
- Auditoria completa por execução
- Suporte a modo dry-run (simulação)

---

## Autor

Projeto desenvolvido como portfólio técnico com foco em Python, automação e IA aplicada.
