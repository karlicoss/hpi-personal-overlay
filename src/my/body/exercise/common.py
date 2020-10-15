from datetime import datetime
from typing import NamedTuple, Optional

# todo each exercise has standard units? not sure
class Exercise(NamedTuple):
    dt: datetime
    kind: str
    reps: Optional[float]
    note: str
