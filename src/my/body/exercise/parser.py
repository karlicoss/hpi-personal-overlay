'''
Some helpers for manual exercise parsing
'''
from functools import lru_cache
import re
from typing import Dict, Optional, List


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


def extract_reps(x: str, kind: Optional[Spec]=None) -> Optional[float]:
    if kind is not None and not kind.has_reps:
        # todo not sure... might want to return None here?
        return 0.0
    x = x.lower()
    # findall wants non-capturing groups...
    res = re.findall(r'\d+(?:\.\d+)?', x)
    if len(res) != 1:
        raise RuntimeError(f'reps: expected single match, got {res}: {x}')
    else:
        return float(res[0])
