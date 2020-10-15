'''
Specs for manual exercise that help with manual parsing
'''
from typing import NamedTuple


class Spec(NamedTuple):
    kind: str
    has_reps: bool = True


S = Spec
ping_pong = S('ping pong'              )
ignore    = S('ignore' , has_reps=False)
sore      = S('sore'   , has_reps=False)

# TODO need to match these & attach to the cardio data
skipping      = S('skipping'     , has_reps=False)
running       = S('running'      , has_reps=False)
cross_trainer = S('cross trainer', has_reps=False)
spinning      = S('spinning'     , has_reps=False)
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
    'calf raises?'  : 'calf raise'       , # TODO is this step up??
    'l[- ]sits?'    : 'l-sit'            ,
    'squats'        : 'squat'            ,
    'pistol squats?': 'pistol squat'     ,
    'chin ups?'     : 'chin-up'          ,

    'pull ups?'     : 'pull-up'          ,
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
    'handstands?'      : None,
    'door strap'       : None,
    'plank'            : None,
}
