"""Example HPI config for the overlay's body modules."""

from pathlib import Path

import pytz


class blood:
    blood_log: Path | str = Path('blood.org')


class body:
    class sleep:
        sleep_log: Path | str = Path('sleep.org')


class exercise:
    workout_log: Path | str = Path('workouts.org')


class weight:
    default_timezone = pytz.timezone('Europe/London')
