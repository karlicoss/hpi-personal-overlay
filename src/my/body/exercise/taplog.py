from typing import Dict, Iterable

from my.core import Res
from my.core.cachew import mcachew
from my.core.orgmode import collect, Table
from my.error import attach_dt
from ... import taplog as T
from . import parser
from .common import Exercise

from my.config import exercise as user_config


def overrides() -> Dict[str, str]:
    '''
    Manual overrides for some entries with typos etc, to simplify further automated parsing
    '''
    # to dump the initial table:
    # sqlite3 taplog.db 'SELECT printf("| %6d | %s |", _id, lower(note)) FROM log WHERE cat1="ex" ORDER BY lower(note)'
    import orgparse
    wlog = orgparse.load(user_config.workout_log)
    [table] = collect(
        wlog,
        lambda n: [] if n.heading != 'Taplog overrides' else [x for x in n.body_rich if isinstance(x, Table)]
    )
    res = {}
    for row in table.as_dicts:
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

        # I've messed up calculating the vest weight at some point
        e.row['note'] = e.row['note'] \
          .replace('15kg' , '10kg' )  \
          .replace('15 kg', '10 kg')

        yield e
    if patched == 0:
        yield RuntimeError('no overrides were matched')


@mcachew
def entries() -> Iterable[Res[Exercise]]:
    for e in _with_overrides():
        if isinstance(e, Exception):
            yield e
            continue
        note = e.note
        kinds = parser.kinds(note)
        if len(kinds) != 1:
            yield attach_dt(
                RuntimeError(f'expected single match, got {kinds}: | {e.id:6} | {note} |'),
                dt=e.timestamp,
            )
            continue
        [k] = kinds

        ew, note = parser.extract_extra(note)

        yield Exercise(
            dt=e.timestamp,
            kind=k.kind,
            reps=e.number, # FIXME sets/tabata
            note=e.note,
            extra_weight=ew,
            src='taplog',
        )


from ...core import stat, Stats
def stats() -> Stats:
    return stat(entries)
