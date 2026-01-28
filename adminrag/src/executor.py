from tools.registry import TOOL_REGISTRY

class ExecutionError(RuntimeError):
    pass

def execute_plan(plan: dict, runtime_context: dict, dry_run: bool = True):
    actions = plan.get("actions", [])
    results = []

    for step in actions:
        tool = step.get("tool")
        args = step.get("args", {}) or {}

        if tool not in TOOL_REGISTRY:
            raise ExecutionError(f"Tool não permitida: {tool}")

        if tool == "export_xlsx":
            args.setdefault("records", runtime_context["records"])
            args.setdefault("out_path", "workspace/saida.xlsx")

        if tool == "write_report_md":
            args.setdefault("title", "Relatório AdminRAG")
            args.setdefault("summary", runtime_context.get("summary", ""))
            args.setdefault("issues", runtime_context.get("issues", []))
            args.setdefault("out_path", "workspace/report.md")

        if dry_run:
            results.append({"tool": tool, "args": args, "status": "dry_run"})
            continue

        fn = TOOL_REGISTRY[tool]
        out = fn(**args)
        results.append({"tool": tool, "args": args, "status": "ok", "output": out})

    return results
