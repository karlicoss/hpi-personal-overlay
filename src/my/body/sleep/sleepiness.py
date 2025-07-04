'''
Sleepiness during the day, manually logged in org-mode
'''

import re

from my import orgmode
from my.core import Stats, make_logger, stat
from my.core.error import extract_error_datetime, set_error_datetime
from my.core.pandas import DataFrameT
from my.core.pandas import check_dataframe as cdf
from my.time.tz import main as TZ

log = make_logger(__name__)


# markers to pick out my sleepiness reports
# TODO need to really simplify this
_markers = [
    # old format, where I tried to assign a 'sleep score'
    r'sleepy (1|2)/3',
    # usually something like 'feeling very sleepy', or 'felt somewhat sleepy', etc
    # TODO exclude 'not'?? e.g. 'not feeling sleepy'
    r'(feeling|was|felt) ((kinda|mildly|somewhat|quite|pretty|very) )?sleepy',
]


def _iter_sleepiness():
    # TODO direct org-mode to pandas would be nice?

    def parse_entry(entry):
        heading = entry.heading
        # manual tag to mark the entry as def containing sleepiness report
        has_tag = 'sleepiness' in entry.tags
        has_marker = any(re.search(m, heading.lower()) is not None for m in _markers)
        if not has_marker and not has_tag:
            yield {'error': f'no marker: {heading}'}
            return

        yield {
            # todo use full + tags?
            'note': heading,
        }

    for l in orgmode.query().all():
        if 'sleepy' not in l.heading.lower():
            continue
        ex = RuntimeError(f'While parsing {l}')
        try:
            dt = l.created
            assert dt is not None
            dt = TZ.localize(dt)
        except Exception as e:
            ex.__cause__ = e
            yield ex
            continue
        set_error_datetime(ex, dt)
        try:
            for r in parse_entry(l):
                r['dt'] = dt
                yield r
        except Exception as e:
            ex.__cause__ = e
            yield ex
            continue


def pre_dataframe():
    # TODO eh, this stuff should be automatic
    for e in _iter_sleepiness():
        if isinstance(e, Exception):
            edt = extract_error_datetime(e)
            yield {
                'dt': edt,
                'error': str(e),
            }
        else:
            yield e


@cdf
def dataframe() -> DataFrameT:
    import pandas as pd  # type: ignore[import-untyped]

    return pd.DataFrame(pre_dataframe())


def stats() -> Stats:
    return stat(dataframe)


# TODO have to fill with defaults? Or do it on receive site?
# TODO ok, so have to do it carefully. need to grab stuff from capture?
# TODO use old taplog entries
#
# TODO(dashboard) correlate both with sleep and exercise?
# also interesting to correlate with sleep last night and sleep next night? a window with delta would def be useful here...
