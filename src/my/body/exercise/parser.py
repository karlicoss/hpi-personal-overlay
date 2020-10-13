'''
Some helpers for manual exercise parsing
'''
import re
from typing import List, Optional


TAGGERS = {
    'ping'          : 'ping pong'        ,

    'push ups?'     : 'push-up'          ,
    'diamond'       : 'diamond push-up'  ,
    'oapu'          : 'one armed push-up',

    'dips'          : 'dip'              ,
    'step ups'      : 'step-up'          ,
    'l[- ]sits?'    : 'l-sit'            ,
    'pistol squats?': 'pistol squat'     ,
    'double under'  : 'skipping'         ,
    'chin ups?'     : 'chin-up'          ,
    'skipping'      : 'skipping'         ,

    'pull ups?'     : 'pull-up'          ,
    'l pull ups?'   : 'l pull-up'        ,

    # todo warnings if there are too many of these?
    'leg raises?'     : None,
    'chest resistance': None,
    'abs? roll(s?|er)': None,
    'handstands?'     : None,
    'door strap'      : None, # ????
    'sore'            : None, # todo not sure if really need to keep?
}


def tags(x: str) -> List[Optional[str]]:
    x = x.lower()
    keys = [
        m for m in TAGGERS
        if re.search(rf'(^|\W){m}(\W|$)', x) is not None
    ]
    # hacky. if there only two, maybe can resolve the tie by picking more specific one?
    if len(keys) == 2:
        [a, b] = keys
        ma = TAGGERS[a]
        mb = TAGGERS[b]
        if ma is not None and mb is not None:
            if ma in mb:
                keys = [b]
            elif mb in ma:
                keys = [a]

    return [TAGGERS[k] for k in keys]
