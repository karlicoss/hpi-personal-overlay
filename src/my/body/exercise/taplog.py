from typing import Dict

from ... import taplog as T
from ...core import Res
from . import parser

from my.config import exercise as user_config


def overrides() -> Dict[str, str]:
    '''
    Manual overrides for some entries with typos etc, to simplify further automated parsing
    '''
    # to dump the initial table:
    # sqlite3 taplog.db 'SELECT printf("| %6d | %s |", _id, lower(note)) FROM log WHERE cat1="ex" ORDER BY lower(note)'
    # todo use orgmode provider directly??
    from porg import Org
    # TODO should use all org notes and just query from them?. it's quite slow...
    wlog = Org.from_file(user_config.workout_log)
    table = wlog.xpath('//org[heading="Taplog overrides"]//table')
    res = {}
    for row in table.lines:
        id   = row['id']
        note = row['note']
        res[id] = note
    return res


def entries() -> Res[T.Entry]:
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


def tagged() -> Res[str]:
    for e in entries():
        if isinstance(e, Exception):
            yield e
            continue
        tags = parser.tags(e.note)
        if len(tags) != 1:
            yield RuntimeError(f'expected single match, got {tags}: | {e.id:6} | {e.note} |')
        else:
            [t] = tags
            yield t


from ...core import stat, Stats
def stats() -> Stats:
    return stat(tagged)
