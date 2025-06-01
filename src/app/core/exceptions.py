class ValidationError(Exception):
    def __init__(self, detail: str | dict[str, str]) -> None:
        self.detail = detail
