from typing import Dict, List
from datetime import datetime
from .RecordRevision import RecordRevision


class Record:
    id: int
    revision: int
    rel_module: int
    values: Dict
    meta: Dict
    rel_namespace: int
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None
    ownded_by: int
    created_by: int
    updated_by: int | None
    deleted_by: int | None
    rel_revisions: List[RecordRevision]

    def __repr__(self) -> str:
        return (
            f"Record(id={self.id}, rel_module={self.rel_module},"
            f" deleted_at={self.deleted_at})"
        )
