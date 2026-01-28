import os
WORKSPACE = os.getenv("WORKSPACE_DIR", "workspace")

def safe_path(rel: str) -> str:
    ab = os.path.abspath(os.path.join(WORKSPACE, rel))
    ws = os.path.abspath(WORKSPACE)
    if not (ab == ws or ab.startswith(ws + os.sep)):
        raise ValueError("Destino fora do workspace.")
    return ab
