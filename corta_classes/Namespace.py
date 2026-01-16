from typing import Dict, List
from datetime import datetime
from .Module import Module


class Namespace:
    ns_id: int
    slug: str
    enabled: bool
    meta: Dict
    name: str
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None
    modules: List[Module] = []

    def __str__(self) -> str:
        return (
            f"Namespace(id={self.ns_id}, slug={self.slug},"
            f"name={self.name}, deleted_at={self.deleted_at})"
        )
