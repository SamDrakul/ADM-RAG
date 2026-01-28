from typing import Callable, Dict
from .spreadsheet import export_xlsx
from .report_tools import write_report_md

TOOL_REGISTRY: Dict[str, Callable] = {
    "export_xlsx": export_xlsx,
    "write_report_md": write_report_md,
}
