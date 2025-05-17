'''
Some helpers for manual exercise parsing
'''
import re
from datetime import datetime
from functools import lru_cache

from .specs import MATCHERS, Spec, ignore


@lru_cache(1)
def _matchers() -> dict[str, Spec]:
    res = {}
    for k, v in MATCHERS.items():
        vv: Spec
        if v is None:
            vv = ignore
        elif isinstance(v, Spec):
            vv = v
        else:
            vv = Spec(v)
        res[k] = vv
    return res


def kinds(x: str) -> list[Spec]:
    M = _matchers()
    x = x.lower()
    keys = [
        m for m in M
        if re.search(rf'(^|\W){m}(\W|$)', x) is not None
    ]
    # hacky. if there only two, maybe can resolve the tie by picking more specific one?
    if len(keys) == 2:
        [a, b] = keys
        ma: Spec = M[a]
        mb: Spec = M[b]
        if ma.kind in mb.kind:
            keys = [b]
        elif mb.kind in ma.kind:
            keys = [a]

    return [M[k] for k in keys]


def extract_sets_reps(x: str, kind: Spec | None=None) -> tuple[int, float]:
    if kind is not None and not kind.has_reps:
        # todo not sure... might want to return None here?
        return (0, 0.0)
    x = x.lower()
    # findall wants non-capturing groups...
    frgx = r'\d+(?:\.\d+)?'
    ## first try 'set x reps' format
    res = re.findall(fr'\d+\s*x\s*{frgx}', x)
    if len(res) == 1:
        # ok, unique match, actually extract sets & reps
        [ss, rs] = re.split('[ x]+', res[0])
        sets = int(ss)
        assert sets > 0
        return sets, float(rs)
    # otherwise, assume it's a single set
    sets = 1
    res = re.findall(frgx, x)
    if len(res) != 1:
        raise RuntimeError(f'reps: expected single match, got {res}: {x}')
    reps = float(res[0])
    return (sets, reps)


from my.core.orgmode import parse_org_datetime


def extract_dt(x: str) -> tuple[datetime | None, str]:
    ress = re.findall(r'\[.*\]', x)
    if len(ress) != 1:
        # todo throw if > 0?
        return (None, x)
    r = ress[0]
    dt = parse_org_datetime(r)
    x = x.replace(r, '') # meh
    return (dt, x)


def extract_extra(x: str) -> tuple[float | None, str]:
    repls = [
        (r'(2x5|4)\s*kg(?: (?:ankle|wrist|elbow))? weights?', ''),
        (r'(\d+)\s*kg( vest)?'                              , ''),
        # todo don't remember if 4kg was 2x2 kg? .. yeah, I think so
        (r'tabata \d+/\d+'                                  , ''),
    ]
    ews = []
    for f, t in repls:
        assert t == '', (f, t)  #  I think I indended to support non-empty replacements later? not sure
        m = re.search(f, x)
        if m is None:
            continue
        b, e = m.span()
        x = x[:b] + x[e:]

        if len(m.groups()) == 0:
            continue

        v = m.group(1)
        v = '10' if v == '2x5' else v # ugh
        ews.append(float(v))


        m = re.search(f, x)
        assert m is None, m
    return (None if len(ews) == 0 else sum(ews), x)


# todo parameterize
def test_extract_sets_reps() -> None:
    from .specs import push_up
    for h, e in [
            ('3x 30 squats', (3, 30))
    ]:
        r = extract_sets_reps(h, kind=push_up)
        assert r == e

def test_extract_extra() -> None:
    ew, rest = extract_extra(
        '60 squats + 2x5kg elbow weights + 10kg vest'
    )
    assert ew == 20.0
    assert rest.strip() == '60 squats +  +'
    ew, rest = extract_extra(
        '3x12 dips slow tabata 60/240 interleaved'
    )
    assert ew is None, ew
    assert rest.strip() == '3x12 dips slow  interleaved'


def test_extract_dt() -> None:
    dt, rest = extract_dt('** [2020-10-10 Sat 10:26] 90 sec')
    assert dt is not None
    assert rest == '**  90 sec'

    dt, rest = extract_dt('whatever [123')
    assert dt is None
    assert rest == 'whatever [123'
