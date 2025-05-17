from datetime import datetime
from typing import NamedTuple


# todo each exercise has standard units? not sure
class Exercise(NamedTuple):
    dt: datetime
    kind: str
    reps: float | None
    note: str

    # todo hmm. hacky, not sure about it...
    extra_weight: float | None = None

    # todo not sure, would be nice to somehow make it automatic?
    src: str = ''

    # todo move to a separate file? volume_model?
    @property
    def volume(self) -> float | None:
        reps = self.reps
        if reps is None:
            return None
        from . import specs

        mult = specs.vmap(self.kind)
        if mult is None:
            return None
        ew = self.extra_weight or 0.0
        # todo kind of mad
        m2 = (WEIGHT + ew) / WEIGHT
        return mult * m2 * reps


# TODO weight should be taken from the weight provider?
WEIGHT = 63.0
