from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

from ...core import Res, LazyLogger
from ...core.cachew import cache_dir
from ...core.common import mcachew
from ...error import attach_dt, sort_res_by
from ... import orgmode as O
from . import parser
from .common import Exercise
# todo might need to merge common and parser?


from porg import Org

logger = LazyLogger(__name__)

_TAG = 'wlog'


def asdt(x) -> Optional[datetime]:
    if x is None:
        return None
    if isinstance(x, datetime):
        return x
    else:
        return None


def _get_outlines(f: Path) -> Iterable[Res[Org]]:
    def extract(cur: Org) -> Iterable[Res[Org]]:
        has_org_tag = _TAG in cur.tags
        if has_org_tag:
            heading = cur.heading
            kinds = parser.kinds(heading)

            if len(kinds) == 1:
                yield cur
                return
            else:
                yield attach_dt(
                    RuntimeError(f'expected single match, got {kinds}: {cur}'),
                    dt=asdt(cur.created),
                )

        for c in cur.children:
            yield from extract(c)

    yield from extract(Org.from_file(f))


# TODO move over tests from private workout provider
def org_to_exercise(o: Org) -> Iterable[Res[Exercise]]:
    heading = o.heading
    [kind] = parser.kinds(heading) # todo kinda annoying to do it twice..

    # FIXME: need shared attributes

    def aux(c: Org):
        dt = asdt(c.created)
        assert dt is not None
        # todo attach dt to the exception?

        heading = c.heading
        heading = parser.extract_extra(heading)

        sets, reps = parser.extract_sets_reps(heading, kind=kind)
        # TODO??
        return Exercise(
            dt=dt,
            kind=kind.kind,
            reps=reps,
            note=heading, # TODO body?
        )

    # FIXME it's possible to have an exrcise with a comment... then it will not be parsed at all
    if len(o.children) > 0:
        # try to process as list of sets (date + rep)
        yield from [aux(c) for c in o.children]
    else:
        # otherwise, treat it as the set log
        yield from [aux(o)]


@mcachew(
    cache_path=lambda f: cache_dir() / __name__ / O._sanitize(f), force_file=True,
    depends_on=lambda f: (f, f.stat().st_mtime),
)
def _from_file(f: Path) -> Iterable[Res[Exercise]]:
    for o in _get_outlines(f):
        if isinstance(o, Exception):
            yield o
        else:
            dt = asdt(o.created)
            try:
                yield from org_to_exercise(o)
            except Exception as e:
                err = RuntimeError(f'while extracting from: {o}')
                err.__cause__ = e
                logger.exception(err)
                yield attach_dt(err, dt=dt)


def _raw() -> Iterable[Res[Exercise]]:
    for p in O.query().files:
        yield from _from_file(p)


def entries() -> Iterable[Res[Exercise]]:
    for note in _raw():
        yield note


from ...core import stat, Stats
def stats() -> Stats:
    return stat(entries)
