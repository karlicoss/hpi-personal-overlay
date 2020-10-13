from datetime import datetime
from typing import NamedTuple

# todo each exercise has standard units? not sure
class Exercise(NamedTuple):
    dt: datetime
    name: str
    reps: float
    note: str
