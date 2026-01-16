from typing import Dict
from datetime import datetime
from typing import List
from .ModuleField import ModuleField
from .Page import Page
from .Record import Record

class Module:
    module_id: int
    rel_namespace: int
    handle: str
    name: str
    meta: Dict
    config: Dict
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None
    fields: List["ModuleField"] = []
    pages: List["Page"] = []
    records: List["Record"] = []

    def __str__(self) -> str:
        return (
            f"Module(id={self.module_id}, handle={self.handle},"
            f" name={self.name}, deleted_at={self.deleted_at})"
        )
