from llm import is_enabled, llm_extract_json

PLANNER_SYSTEM = (
    "Você é um planejador de automações administrativas.\n"
    "Retorne APENAS JSON válido.\n"
    "Objetivo: montar um plano de ações usando ferramentas permitidas.\n"
    "Ferramentas permitidas:\n"
    "- export_xlsx(records, out_path)\n"
    "- write_report_md(title, summary, issues, out_path)\n"
    "O plano deve ser: {\"actions\": [{\"tool\": \"...\", \"args\": {...}}, ...]}\n"
    "Nunca invente ferramentas fora da lista.\n"
)

async def plan_actions(goal: str, context: dict):
    if not is_enabled():
        return {
            "actions": [
                {"tool": "export_xlsx", "args": {"out_path": "workspace/saida.xlsx"}},
                {"tool": "write_report_md", "args": {"title": "Relatório AdminRAG", "out_path": "workspace/report.md"}},
            ]
        }

    user = (
        f"Meta do usuário: {goal}\n\n"
        f"Contexto disponível (resumo):\n{context}\n\n"
        "Gere um plano usando somente ferramentas permitidas."
    )
    return await llm_extract_json(system=PLANNER_SYSTEM, user=user)
