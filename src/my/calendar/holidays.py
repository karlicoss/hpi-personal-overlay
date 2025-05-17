from my.core.experimental import import_original_module

_ORIG = import_original_module(__name__, __file__, star=True, globals=globals())

from datetime import datetime, date
from typing import Union

DateIsh = Union[datetime, date, str]


is_holiday_orig = _ORIG.is_holiday
def is_holiday(d: DateIsh) -> bool:
    # if it's a public holiday, definitely a holiday?
    if is_holiday_orig(d):
        return True
    # then check private data of days off work
    if is_day_off_work(d):
        return True
    return False
_ORIG.is_holiday = is_holiday  # type: ignore[attr-defined]
# NOTE: without overriding the original, the functions from M itself are capturing the old function?
# need to test it...

###

from datetime import datetime, date, datetime, timedelta
from functools import lru_cache
from typing import Iterable, Tuple, List
import re

def is_day_off_work(d: DateIsh) -> bool:
    day = _ORIG.as_date(d)
    return day in _days_off_work()


@lru_cache(1)
def _days_off_work() -> List[date]:
    return list(_iter_days_off_work())


def _iter_work_data() -> Iterable[Tuple[date, int]]:
    from my.config.holidays_data import HOLIDAYS_DATA   # type: ignore[import-not-found]
    emitted = 0
    for x in HOLIDAYS_DATA.splitlines():
        m = re.search(r'(\d\d/\d\d/\d\d\d\d)(.*)-(\d+.\d+) days \d+.\d+ days', x)
        if m is None:
            continue
        (ds, cmnt, dayss) = m.groups()
        if 'carry over' in cmnt:
            continue

        d = datetime.strptime(ds, '%d/%m/%Y').date()
        dd, u = dayss.split('.')
        assert u == '00' # TODO meh

        yield d, int(dd)
        emitted += 1
    assert emitted > 5 # arbitrary, just a sanity check.. (todo move to tests?)


def _iter_days_off_work() -> Iterable[date]:
    # TODO wtf is it doing?...
    for d, span in _iter_work_data():
        dd = d
        while span > 0:
            # only count it if it wasnt' a public holiday/weekend already
            if _ORIG._calendar().is_working_day(dd):
                yield dd
                span -= 1
            dd += timedelta(days=1)
