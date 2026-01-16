from typing import Dict
from datetime import datetime


class PageLayout:
    id: int
    handle: str
    page_id: int
    parent_id: int
    rel_namespace: int
    weight: int
    meta: Dict
    config: Dict
    blocks: Dict
    owned_by: int
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None

    def __repr__(self) -> str:
        return (
            f"PageLayout(layout_id={self.id}, "
            f"page_id={self.page_id}, deleted_at={self.deleted_at})"
        )
