from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Dict, Iterable, Optional

from more_itertools import ilen

from ...core import Res, LazyLogger
from ...core.cachew import cache_dir
from ...core.common import mcachew
from ...time.tz import main as TZ
from ...error import attach_dt, sort_res_by
from ... import orgmode as O
from . import parser
from .common import Exercise
# todo might need to merge common and parser?

import orgparse
from orgparse import OrgNode

logger = LazyLogger(__name__)

_TAG = 'wlog'


def asdt(x) -> Optional[datetime]:
    if x is None:
        return None
    if isinstance(x, datetime):
        return TZ.localize(x)
    else:
        return None


# helper to attach error context
def parse_error(e: Exception, org: OrgNode, *, dt: Optional[datetime]=None) -> Exception:
    if dt is None:
        dt, _ = O._created(org)
        dt = asdt(dt)
    ex = RuntimeError(f'While parsing {org.env.filename}:{org.linenumber} {org.heading}')
    ex.__cause__ = e
    return attach_dt(ex, dt=dt)


def _get_outlines(f: Path) -> Iterable[Res[OrgNode]]:
    def extract(cur: OrgNode) -> Iterable[Res[OrgNode]]:
        has_org_tag = _TAG in cur.tags
        if has_org_tag:
            heading = cur.heading
            kinds = parser.kinds(heading)

            if len(kinds) == 1:
                yield cur
                return
            else:
                yield parse_error(
                    RuntimeError(f'expected single match, got {kinds}'),
                    org=cur,
                )

        for c in cur.children:
            yield from extract(c)

    yield from extract(orgparse.load(f))


# TODO move over tests from private workout provider
def org_to_exercise(o: OrgNode) -> Iterable[Res[Exercise]]:
    heading = o.heading
    [kind] = parser.kinds(heading) # todo kinda annoying to do it twice..

    # FIXME: need shared attributes?
    cdt, _, = O._created(o)
    pdt = asdt(cdt)

    def aux(heading: str) -> Iterable[Res[Exercise]]:
        dt, heading = parser.extract_dt(heading)
        dt = asdt(dt) # meh
        ew, heading = parser.extract_extra(heading)
        dt = dt or pdt
        if dt is None:
            yield parse_error(RuntimeError('No datetime'), org=o)
            return
        try:
            sets, reps = parser.extract_sets_reps(heading, kind=kind)
        except Exception as e:
            yield parse_error(e, org=o, dt=dt)
            return
        # TODO hmm. if exercise doesn't have reps, then it won't be emitted at all (sets would be 0)
        for _ in range(sets):
            yield Exercise(
                dt=dt,
                kind=kind.kind,
                reps=reps,
                note=heading, # todo attach body?
                extra_weight=ew,
                src='orgmode',
            )

    cs = o.body + '\n'.join(x.heading + '\n' + x.body for x in o[1:]) # all descendants
    lines = [l.strip() for l in cs.splitlines() if len(l.strip()) > 0]

    # try to process as list of sets (date + rep)
    body_res = list(chain.from_iterable(aux(l) for l in lines))
    body_ok = ilen(x for x in body_res if isinstance(x, Exercise))

    # or, treat it as the sets x rep log
    head_res = list(aux(heading))
    head_ok = ilen(x for x in head_res if isinstance(x, Exercise))

    if body_ok < 2: # kinda arbitrary, but I guess if there are no numbers in the body, it's unlinkely
        yield from head_res
        return
    if head_ok == 0:
        # ok, everything must have been logged in the body?
        yield from (r for r in body_res if not isinstance(r, Exception))
        return
    # otherwise something's not quite right.. just emit the errors
    yield from (r for r in head_res + body_res if isinstance(r, Exception))
    yield parse_error(RuntimeError(f'Confusing parsing:\n{head_res}\n{body_res}'), org=o)


@mcachew(
    cache_path=lambda f: cache_dir() / __name__ / O._sanitize(f), force_file=True,
    depends_on=lambda f: (f, f.stat().st_mtime),
)
def _from_file(f: Path) -> Iterable[Res[Exercise]]:
    for o in _get_outlines(f):
        if isinstance(o, Exception):
            yield o
        else:
            try:
                yield from org_to_exercise(o)
            except Exception as e:
                logger.exception(e)
                yield parse_error(RuntimeError('Unhandled error'), org=o)


def _raw() -> Iterable[Res[Exercise]]:
    for p in O.query().files:
        yield from _from_file(p)


def entries() -> Iterable[Res[Exercise]]:
    for note in _raw():
        yield note


from ...core import stat, Stats
def stats() -> Stats:
    return stat(entries)


### tests

def test_org_to_exercise() -> None:
    s = '''
* hollow rocks :wlog:
** [2020-10-10 Sat 10:26] 90 sec
** [2020-10-10 Sat 10:38] 90 sec
** [2020-10-10 Sat 10:47] 90 sec
** [2020-10-10 Sat 10:56] 90 sec
* push ups diamond :wlog:
this should be handled by workout processor.. need to test?
- [2020-10-04 Sun 13:45] 25
- [2020-10-04 Sun 14:00] 25
- [2020-10-04 Sun 14:14] 21.5F
- [2020-10-04 Sun 14:33] 16.5F
* [2019-01-05 Sat 13:03] static hollow leg holds tabata 120/240 :wlog:good:
** 120 secs
** 90 secs (gave up)
** 120 secs
* [2018-10-04 Thu 07:46] 20 pu diamond :wlog:
* [2018-10-04 Thu 07:50] 30.5F pu wide
'''
    os = orgparse.loads(s)
    o = os.children[0]
    xx = list(org_to_exercise(o))
    for x in xx:
        assert not isinstance(x, Exception)
        assert x.dt is not None
        assert x.reps == 90

    o = os.children[1]
    yy = list(org_to_exercise(o))
    assert len(yy) == 4
    for y in yy:
        assert not isinstance(y, Exception)
        assert y.dt is not None
        reps = y.reps
        assert reps is not None
        assert reps > 15 # todo more specific tests
    o = os.children[2]
    zz = list(org_to_exercise(o))
    [a, b, c] = zz
    assert isinstance(b, Exercise)
    assert isinstance(c, Exercise)
    assert b.reps == 90
    assert c.reps == 120

    o = os.children[3]
    zz = list(org_to_exercise(o))
    [x] = zz
    assert isinstance(x, Exercise)
    assert x.reps == 20

    o = os.children[4]
    zz = list(org_to_exercise(o))
    [x] = zz
    assert isinstance(x, Exercise)
    assert x.reps == 30.5
