from pathlib import Path
from typing import Dict, Iterable

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
                    dt=cur.created,
                )

        for c in cur.children:
            yield from extract(c)

    yield from extract(Org.from_file(f))


# TODO move over tests from private workout provider
def org_to_exercise(o: Org) -> Iterable[Res[Exercise]]:
    heading = o.heading
    [kind] = parser.kinds(heading) # todo kinda annoying to do it twice..

    if len(o.children) > 0:
        # try to process as list of sets (date + rep)
        exs = []
        for c in o.children:
            dt = c.created
            assert dt is not None
            # todo attach dt to the exception?
            reps = parser.extract_reps(c.heading)
            exs.append(Exercise(
                dt=dt,
                name=kind,
                reps=reps,
                note=c.heading, # todo + body?
            ))
        yield from exs
    else:
        # otherwise, treat it as the set log
        dt = o.created
        assert dt is not None
        reps = parser.extract_reps(heading)
        yield Exercise(
            dt=dt,
            name=kind,
            reps=reps,
            note=heading,
        )


@mcachew(
    cache_path=lambda f: cache_dir() / __name__ / O._sanitize(f), force_file=True,
    depends_on=lambda f: (f, f.stat().st_mtime),
)
def _from_file(f: Path) -> Iterable[Res[Exercise]]:
    for o in _get_outlines(f):
        if isinstance(o, Exception):
            yield o
        else:
            dt = o.created
            try:
                yield from org_to_exercise(o)
            except Exception as e:
                err = RuntimeError(f'while extracting from: {o}')
                err.__cause__ = e
                logger.exception(err)
                yield attach_dt(err, dt=dt)


def _raw() -> Iterable[Res[O.OrgNote]]:
    for p in O.query().files:
        yield from _from_file(p)


def entries() -> Iterable[Res[Exercise]]:
    for note in _raw():
        yield note


from ...core import stat, Stats
def stats() -> Stats:
    return stat(entries)
