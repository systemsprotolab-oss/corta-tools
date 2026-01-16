from typing import Dict, List
from .PageLayout import PageLayout


class Page:
    id: int
    rel_namespace: int
    title: str
    handle: str
    self_id: int
    rel_module: int
    meta: Dict
    config: Dict
    blocks: Dict
    visible: bool
    weight: int
    description: str
    created_at: str
    updated_at: str
    deleted_at: str
    layouts: List[PageLayout] = []

    def __repr__(self) -> str:
        return (
            f"Page(id={self.id}, rel_namespace={self.rel_namespace},"
            f"title={self.title}, deleted_at={self.deleted_at})"
        )
