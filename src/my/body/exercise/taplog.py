from typing import Dict, Iterable

from ...core import Res
from ...core.common import mcachew
from ...error import attach_dt
from ... import taplog as T
from . import parser, common

from my.config import exercise as user_config


def overrides() -> Dict[str, str]:
    '''
    Manual overrides for some entries with typos etc, to simplify further automated parsing
    '''
    # to dump the initial table:
    # sqlite3 taplog.db 'SELECT printf("| %6d | %s |", _id, lower(note)) FROM log WHERE cat1="ex" ORDER BY lower(note)'
    # todo use orgmode provider directly??
    from porg import Org
    # todo should use all org notes and just query from them?. it's quite slow...
    wlog = Org.from_file(user_config.workout_log)
    table = wlog.xpath_all('//org[heading="Taplog overrides"]//table')[0]
    res = {}
    for row in table.lines:
        id   = row['id']
        note = row['note']
        res[id] = note
    return res


def _with_overrides() -> Iterable[Res[T.Entry]]:
    ov = overrides()
    patched = 0
    for e in T.by_button('ex'):
        o = ov.get(e.id, None)
        if o is not None:
            e.row['note'] = o
            patched += 1
        yield e
    if patched == 0:
        yield RuntimeError('no overrides were matched')


@mcachew
def entries() -> Iterable[Res[common.Exercise]]:
    for e in _with_overrides():
        if isinstance(e, Exception):
            yield e
            continue
        kinds = parser.kinds(e.note)
        if len(kinds) != 1:
            yield attach_dt(
                RuntimeError(f'expected single match, got {kinds}: | {e.id:6} | {e.note} |'),
                dt=e.timestamp,
            )
        else:
            [k] = kinds
            yield common.Exercise(
                dt=e.timestamp,
                name=k,
                reps=e.number, # FIXME sets/tabata
                note=e.note,
            )


from ...core import stat, Stats
def stats() -> Stats:
    return stat(entries)
