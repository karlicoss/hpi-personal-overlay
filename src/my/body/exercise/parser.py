'''
Some helpers for manual exercise parsing
'''
import re
from typing import List, Optional


MATCHERS = {
    'ping'          : 'ping pong'        ,

    'push ups?'     : 'push-up'          ,
    'diamond'       : 'diamond push-up'  ,
    'oapu'          : 'one armed push-up',

    'dips'          : 'dip'              ,
    'step ups'      : 'step-up'          ,
    'l[- ]sits?'    : 'l-sit'            ,
    'squats'        : 'squat'            ,
    'pistol squats?': 'pistol squat'     ,
    'double under'  : 'skipping'         ,
    'chin ups?'     : 'chin-up'          ,
    'skipping'      : 'skipping'         ,

    'pull ups?'     : 'pull-up'          ,
    'l pull ups?'   : 'l pull-up'        ,

    'hollow rocks?' : 'hollow rock'      ,

    # todo warnings if there are too many of these?
    'leg raises?'     : None,
    'chest resistance': None,
    'abs? roll(s?|er)': None,
    'handstands?'     : None,
    'door strap'      : None, # ????
    'sore'            : None, # todo not sure if really need to keep?
}


def kinds(x: str) -> List[Optional[str]]:
    x = x.lower()
    keys = [
        m for m in MATCHERS
        if re.search(rf'(^|\W){m}(\W|$)', x) is not None
    ]
    # hacky. if there only two, maybe can resolve the tie by picking more specific one?
    if len(keys) == 2:
        [a, b] = keys
        ma = MATCHERS[a]
        mb = MATCHERS[b]
        if ma is not None and mb is not None:
            if ma in mb:
                keys = [b]
            elif mb in ma:
                keys = [a]

    return [MATCHERS[k] for k in keys]


# todo exercise hint?? to tell apart seconds & reps
def extract_reps(x: str) -> float:
    x = x.lower()
    # findall wants non-capturing groups...
    res = re.findall(r'\d+(?:\.\d+)?', x)
    if len(res) != 1:
        raise RuntimeError(f'expected single match, got {res}: {x}')
    else:
        return float(res[0])
