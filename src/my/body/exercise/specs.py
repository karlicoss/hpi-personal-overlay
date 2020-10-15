'''
Specs for manual exercise that help with manual parsing
'''
from typing import NamedTuple


class Spec(NamedTuple):
    kind: str
    has_reps: bool = True


S = Spec
ping_pong = S('ping pong'             )
skipping  = S('skipping'              )
ignore    = S('ignore', has_reps=False)
sore      = S('sore'  , has_reps=False)
del S


from typing import Dict, Union, Optional
SpecIsh = Union[Spec, str]
# None means ignore
MATCHERS: Dict[str, Optional[SpecIsh]] = {
    'ping'          : ping_pong          ,

    'push ups?'     : 'push-up'          ,
    'diamond'       : 'diamond push-up'  ,
    'oapu'          : 'one armed push-up',

    'dips'          : 'dip'              ,
    'step ups'      : 'step-up'          ,
    'l[- ]sits?'    : 'l-sit'            ,
    'squats'        : 'squat'            ,
    'pistol squats?': 'pistol squat'     ,
    'chin ups?'     : 'chin-up'          ,
    'double under'  : skipping           ,
    'skipping'      : skipping           ,

    'pull ups?'     : 'pull-up'          ,
    'l pull ups?'   : 'l pull-up'        ,

    'hollow rocks?' : 'hollow rock'      ,

    # todo warnings if there are too many of these?
    'leg raises?'     : None,
    'chest resistance': None,
    'abs? roll(s?|er)': None,
    'handstands?'     : None,
    'door strap'      : None, # ????
    'sore'            : sore,
}

