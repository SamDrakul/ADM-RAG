from datetime import datetime
from .safety import safe_path

def write_report_md(title: str, summary: str, issues: list, out_path: str = "report.md"):
    p = safe_path(out_path)
    now = datetime.utcnow().isoformat()
    md = f"# {title}\n\nGerado em: {now} UTC\n\n## Resumo\n{summary}\n\n## Pendências/Issues\n"
    if not issues:
        md += "- (nenhuma)\n"
    else:
        for it in issues:
            md += f"- {it}\n"
    with open(p, "w", encoding="utf-8") as f:
        f.write(md)
    return {"ok": True, "report": out_path}
