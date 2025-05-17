'''
Manually tracked sleep data: sleepiness, dreams, whether I woke up on time, grogginess during sleep, etc.
'''

import re
from collections.abc import Iterator
from datetime import datetime
from typing import NamedTuple

import my.config
from my.core import LazyLogger, Stats, stat
from my.core.error import Res, extract_error_datetime, set_error_datetime
from my.core.orgmode import one_table, parse_org_datetime
from my.core.pandas import DataFrameT
from my.core.pandas import check_dataframe as cdf
from my.time.tz import main as TZ

log = LazyLogger(__name__)


class Entry(NamedTuple):
    dt: datetime
    # TODO fuck, this frozenset is pretty confusing...
    dreams: float
    mental: float
    wakeup: str


Result = Res[Entry]


def isint(s: str):
    try:
        int(s)
    except:
        return False
    else:
        return True


def rpunct(s: str) -> str:
    return re.sub(r'[.,]', ' ', s)


# fmt: off
_xxx = [
    ([]    , None),
    ([0]   , 0.0),
    ([1]   , 1.0),
    ([2]   , 2.0),
    ([1, 2], 1.5),
]
# fmt: on

_dream_score_map = {frozenset(l): score for l, score in _xxx}


def iter_sleep_table() -> Iterator[Result]:
    # TODO yield error if time is weird?
    # TODO make sure time is unique

    def parse_row(row):
        dreamss = row['dreams']
        mentals = row['mental']
        wakeup = row['wakeup']
        dreams = set(rpunct(dreamss).split())
        extra = dreams.difference({'0', '1', '2'})
        assert len(extra) == 0, extra
        rdreams = _dream_score_map.get(frozenset({int(x) for x in dreams}), None)
        assert rdreams is not None

        vals = {'0', '1', '2'}
        toks = set(rpunct(mentals).split())
        nums = list(toks.intersection(vals))
        assert len(nums) == 1, nums

        rmental = float(nums[0])
        extra = toks.difference(vals)
        if rmental == 1.0 and 'sleepy' in extra:
            rmental -= 0.5  # meh
        return (rdreams, rmental, wakeup)

    user_config = my.config.body.sleep  # type: ignore[attr-defined]

    import orgparse  # TODO add to REQUIRES?

    o = orgparse.load(user_config.sleep_log)
    table = one_table(o)
    # TODO use TypedTable, similar to cross_trainder df?
    for row in table.as_dicts:
        ex = RuntimeError(f'While parsing {row}')
        # first try to determine the timestamp (for better exception message)
        try:
            dt = parse_org_datetime(row['date'])
            # todo hmm. not sure if should localize here... maybe make a version of localize that falls back on utc?
            dt = TZ.localize(dt)
        except Exception as e:
            ex.__cause__ = e
            yield ex
            continue

        set_error_datetime(ex, dt)

        try:
            (dreams, mental, wakeup) = parse_row(row)
        except Exception as e:
            ex.__cause__ = e
            yield ex
            continue

        yield Entry(
            dt=dt,
            dreams=dreams,
            mental=mental,
            wakeup=wakeup,
        )


# todo make sure cachew can handle dicts with dt? not sure
def pre_dataframe():
    for e in iter_sleep_table():
        if isinstance(e, Exception):
            # import traceback
            # traceback.print_exception(Exception, e, None)
            # TODO how to force log.exception to always log traceback??
            # log.exception(e)
            # TODO attach traceback to error in dataframe as well?
            edt = extract_error_datetime(e)
            yield {
                'dt': edt,
                'error': str(e),
            }
        else:
            # TODO just dump the dict?
            yield {
                'dt': e.dt,
                'dreams': e.dreams,
                'mental': e.mental,
            }


# TODO make sure error column is always preset... maybe also add to cdf?
# also it needs to be str, so contain None, not NaN?
@cdf
def dataframe() -> DataFrameT:
    import pandas as pd  # type: ignore[import-untyped]

    return pd.DataFrame(pre_dataframe())
    # TODO make sure date is unique and warn?
    # maybe could be part of cdf?


def stats() -> Stats:
    return stat(dataframe)


# TODO maybe need correlate function for two dt indexed dataframes?
# that way could somewhat simplify error handling?
