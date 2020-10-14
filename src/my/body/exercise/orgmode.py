from typing import Dict, Iterable

from ...core import Res
from ...core.common import mcachew
from ...error import attach_dt, sort_res_by
from ... import orgmode as O
from . import parser, common


def _raw() -> Iterable[Res[O.OrgNote]]:
    from porg import Org

    def extract(cur: Org) -> Iterable[Res[Org]]:
        has_org_tag = 'wlog' in cur.tags
        if has_org_tag:
            heading = cur.heading
            kinds = parser.kinds(heading)

            if len(kinds) == 1:
                yield cur
                return
            else:
                yield attach_dt(
                    RuntimeError(f'expected single match, got {kinds}: {cur}'),
                    dt=cur.created,
                )

        for c in cur.children:
            yield from extract(c)

    for p in O.query().files:
        for e in extract(Org.from_file(p)):
            if isinstance(e, Exception):
                yield e
            else:
                yield O.to_note(e)


def entries() -> Iterable[Res[common.Exercise]]:
    for note in _raw():
        yield note


from ...core import stat, Stats
def stats() -> Stats:
    return stat(entries)
