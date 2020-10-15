'''
Some helpers for manual exercise parsing
'''
from functools import lru_cache
import re
from typing import Dict, Optional, List, Tuple


from .specs import Spec, MATCHERS, ignore


@lru_cache(1)
def _matchers() -> Dict[str, Spec]:
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


def kinds(x: str) -> List[Spec]:
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


def extract_sets_reps(x: str, kind: Optional[Spec]=None) -> Tuple[int, float]:
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
        return int(ss), float(rs)
    # otherwise, assume it's a single set
    sets = 1
    res = re.findall(frgx, x)
    if len(res) != 1:
        raise RuntimeError(f'reps: expected single match, got {res}: {x}')
    reps = float(res[0])
    return (sets, reps)


def extract_extra(x: str) -> str:
    repls = [
        (r'(\d+)\s*kg vest'                                 , ''),
        # TODO don't remember if 4kg was 2x2 kg?
        (r'(2x5|4)\s*kg(?: (?:ankle|wrist|elbow))? weights?', ''),
        (r'tabata \d+/\d+'                                  , ''),
    ]
    for f, t in repls:
        x = re.sub(f, t, x)
    return x


# todo parameterize
def test_extract_sets_reps() -> None:
    from .specs import push_up
    for h, e in [
            ('3x 30 squats', (3, 30))
    ]:
        r = extract_sets_reps(h, kind=push_up)
        assert r == e

def test_extract_extra() -> None:
    assert extract_extra(
        '60 squats + 2x5kg elbow weights + 10kg vest'
    ).strip() == '60 squats +  +'
    assert extract_extra(
        '3x12 dips slow tabata 60/240 interleaved'
    ).strip() == '3x12 dips slow  interleaved'
