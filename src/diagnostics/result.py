from dataclasses import dataclass

@dataclass(frozen=True)
class Result:
    property: str
    status: str
    reasons: tuple[str, ...]

    def __str__(self) -> str:
        return f'{self.property}: {self.status}' + ('\n  ' + '\n  '.join(self.reasons) if self.reasons else '')
