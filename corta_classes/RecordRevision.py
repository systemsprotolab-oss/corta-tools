from datetime import datetime
from typing import Dict


class RecordRevision:
    id: int
    ts: datetime
    rel_resource: int
    revision: int
    operation: str
    rel_user: int
    delta: Dict | None
    comment: str
    
    def __repr__(self) -> str:
        return (
            f"RecordRevision(id={self.id}, rel_resource={self.rel_resource},"
            f" revision={self.revision}, operation={self.operation})"
        )
