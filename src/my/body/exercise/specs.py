'''
Specs for manual exercise that help with manual parsing
'''
from typing import NamedTuple, Dict, Union, Optional


class Spec(NamedTuple):
    kind: str
    has_reps: bool = True


# helper to make sure specs are not duplicated with different args
_specs: Dict[str, Spec] = {}
def spec(kind: str, **kwargs) -> Spec:
    c = _specs.get(kind, None)
    if c is not None:
        return c
    else:
        s = Spec(kind, **kwargs)
        _specs[kind] = s
        return s


S = spec
push_up         = S('push-up')
push_up_diamond = S('diamond push-up')
squat           = S('squat'  )
dip             = S('dip'    )
pull_up         = S('pull-up')
chin_up         = S('chin-up')

ignore    = S('ignore' , has_reps=False)
sore      = S('sore'   , has_reps=False)

# TODO need to match these & attach to the cardio data
ping_pong     = S('ping pong'                    )
skipping      = S('skipping'     , has_reps=False)
running       = S('running'      , has_reps=False)
cross_trainer = S('cross trainer', has_reps=False)
spinning      = S('spinning'     , has_reps=False)


SpecIsh = Union[Spec, str]
# None means ignore
MATCHERS: Dict[str, Optional[SpecIsh]] = {
    'ping'          : ping_pong          ,

    'push ups?'     : push_up            ,
    'diamond'       : push_up_diamond    ,
    'oapu'          : 'one armed push-up',

    'dips'          : dip                ,
    'step ups'      : 'step-up'          ,
    'calf raises?'  : 'calf raise'       , # TODO is this step up??
    'l[- ]sits?'    : 'l-sit'            ,
    'squats'        : squat              ,
    'pistol squats?': 'pistol squat'     ,
    'chin ups?'     : chin_up            ,

    'pull ups?'     : pull_up            ,
    'l pull ups?'   : 'l pull-up'        ,

    'hollow rocks?' : 'hollow rock'      ,
    'knee raises'   : 'knee raise'       ,

    'double under'  : skipping           ,
    'skipping'      : skipping           ,
    'running'       : running            ,
    'treadmill'     : running            ,
    'elliptical'    : cross_trainer      ,
    'spinning'      : spinning           ,

    'sore'            : sore,
    'soredness'       : sore,

    # handle these later
    # todo warnings if there are too many of these?
    'static semi squat': None,
    'leg raises?'      : None,
    'chest resistance' : None,
    'abs? roll(s?|er)' : None,
    'abs? wheel'       : None,
    'handstands?'      : None,
    'door strap'       : None,
    'plank'            : None,
}


# a completely made up model: equate the maxium reps as the 'maximum' effort I can exert 'in general
max_reps: Dict[Spec, float] = {
    push_up: 30.0,
    push_up_diamond: 30.0,
    pull_up: 15.0, # FIXME 13
    chin_up: 15.0, # FIXME 13
    dip    : 15.0, # FIXME 15?
    squat  : 38.0, # FIXME 90.0,
}
# then one rep is the inverse (with a multiplier to make numbers nicer)
one_rep: Dict[Spec, float] = {
    k: 15.0 / v
    for k, v in max_reps.items()
}

from functools import lru_cache
@lru_cache(None)
def vmap(x: SpecIsh) -> Optional[float]:
    if isinstance(x, str):
        s = spec(x)
    else:
        s = x
    return one_rep.get(s, None)

del S
