from datetime import datetime
from typing import NamedTuple, Optional

# todo each exercise has standard units? not sure
class Exercise(NamedTuple):
    dt: datetime
    kind: str
    reps: Optional[float]
    note: str

    @property
    def volume(self) -> Optional[float]:
        reps = self.reps
        if reps is None:
            return None
        from . import specs
        mult = specs.vmap(self.kind)
        if mult is None:
            return None
        return mult * reps
