import os
from pathlib import Path

from ruamel.yaml import YAML

DATADIR = Path(__file__).parent.parent / "data"
yaml = YAML(typ="safe")

def resource_kwargs(item: dict, id_key: str = "import_id") -> dict[str, str]:
    kwargs = {"protect": item.get("protect", True)}
    if os.getenv("PULUMI_IMPORT") and item.get(id_key):
        kwargs["import_"] = item[id_key]
    return kwargs
