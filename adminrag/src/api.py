import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from ingest_knowledge import ingest_knowledge
from pipeline import process_inbox
from planner import plan_actions
from executor import execute_plan
from tools.auditlog import write_audit

app = FastAPI(title="AdminRAG")

class RunRequest(BaseModel):
    inbox_dir: str = "inbox"
    goal: str = "Extrair CPF do pagador e confirmar pagamento de boletos"
    dry_run: bool = True

@app.post("/ingest-knowledge")
def ingest_knowledge_endpoint():
    return ingest_knowledge()

@app.post("/run")
async def run(req: RunRequest):
    run_id = str(uuid.uuid4())[:8]

    results = await process_inbox(req.inbox_dir)
    records = [r.record.model_dump() for r in results]

    issues_list = []
    for r in results:
        issues_list.append(f"{r.record.file_name}: " + "; ".join(r.issues))

    runtime_context = {
        "records": records,
        "issues": issues_list,
        "summary": f"Processados {len(records)} arquivos do inbox. Dry-run={req.dry_run}",
    }

    plan = await plan_actions(req.goal, context={
        "count": len(records),
        "examples": records[:1],
        "issues_sample": issues_list[:3]
    })

    actions = execute_plan(plan, runtime_context=runtime_context, dry_run=req.dry_run)

    audit = write_audit(run_id, {
        "goal": req.goal,
        "dry_run": req.dry_run,
        "records_count": len(records),
        "plan": plan,
        "actions": actions,
        "issues_sample": issues_list[:10],
    })

    return {
        "run_id": run_id,
        "records": records,
        "plan": plan,
        "actions": actions,
        "audit": audit,
    }
