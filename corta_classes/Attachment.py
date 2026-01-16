class Attachment:
    db_id: int
    namespace: int
    url: str
    preview_url: str
    

    def __str__(self) -> str:
        return (
            f"Attachment(id={self.db_id}, url={self.url},"
            f"preview_url={self.preview_url},)"
            f"url={self.url}"
        )
