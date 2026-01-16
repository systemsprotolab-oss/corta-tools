from datetime import datetime


class ModuleField:
    id: int
    rel_module: int
    place: str
    kind: str
    options: dict
    name: str
    label: str
    config: dict
    is_required: bool
    is_multi: bool
    default_value: str
    expression: str
    created_at: datetime | None
    updated_at: datetime | None
    deletad_at: datetime | None

    def __str__(self) -> str:
        return (
            f"ModuleField(id={self.id}, rel_module={self.rel_module},"
            f"name={self.name}, label={self.label},"
            f" deleted_at={self.deletad_at})"
        )
