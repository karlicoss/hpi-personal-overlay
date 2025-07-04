'''
Specs for manual exercise that help with manual parsing
'''

from functools import lru_cache
from typing import NamedTuple


class Spec(NamedTuple):
    kind: str
    has_reps: bool = True


S = Spec
# fmt: off
push_up         = S('push-up')
push_up_diamond = S('diamond push-up')
push_up_wide    = S('wide push-up')
squat           = S('squat'  )
squat_pistol    = S('pistol squat')
dip             = S('dip'    )
pull_up         = S('pull-up')
pull_up_l       = S('l pull-up')
chin_up         = S('chin-up')
hollow_rock     = S('hollow rock')
hollow_leg_hold = S('hollow leg hold')
knee_raise      = S('knee raise')
calf_raise      = S('calf raise') # TODO is this step up???
step_up         = S('step-up')

squat_hold      = S('squat hold')

ignore    = S('ignore' , has_reps=False)
sore      = S('sore'   , has_reps=False)

# TODO need to match these & attach to the cardio data
ping_pong     = S('ping pong'                    )
skipping      = S('skipping'     , has_reps=False)
running       = S('running'      , has_reps=False)
cross_trainer = S('cross trainer', has_reps=False)
spinning      = S('spinning'     , has_reps=False)
# fmt: on


SpecIsh = Spec | str

# fmt: off
# None means ignore
MATCHERS: dict[str, SpecIsh | None] = {
    'ping'          : ping_pong          ,

    'push ups?'     : push_up            ,
    'diamond'       : push_up_diamond    ,
    'oapu'          : 'one armed push-up',
    # ' pu ' # TODO ugh. they need to be ordered??
    'pu wide'       : push_up_wide       ,
    'push ups? wide': push_up_wide       ,

    'dips'          : dip                ,
    'step ups'      : step_up            ,
    'calf raises?'  : calf_raise         ,
    'l[- ]sits?'    : 'l-sit'            ,
    'squats'        : squat              ,
    'pistol squats?': squat_pistol       ,
    'chin ups?'     : chin_up            ,

    'pull ups?'     : pull_up            ,
    'l pull ups?'   : pull_up_l          ,

    'knee raises'   : knee_raise         ,

    'hollow rocks?' : hollow_rock        ,
    'hollow leg holds?': hollow_leg_hold ,

    'double under'  : skipping           ,
    'skipping'      : skipping           ,
    'running'       : running            ,
    'treadmill'     : running            ,
    'elliptical'    : cross_trainer      ,
    'spinning'      : spinning           ,

    'squat holds?'  : squat_hold         ,

    'sore'            : sore,
    'soredness'       : sore,

    # handle these later
    # todo warnings if there are too many of these?
    'leg raises?'      : None,
    'chest resistance' : None,
    'abs? roll(s?|er)' : None,
    'abs? wheel'       : None,
    'handstands?'      : None,
    'door strap'       : None,
    'plank'            : None,
}
# fmt: on


# fmt: off
# a completely made up model: equate the maxium reps as the 'maximum' effort I can exert 'in general
max_reps: dict[Spec, float] = {
    push_up: 30.0,
    push_up_diamond: 30.0,
    push_up_wide: 40.0,
    pull_up  : 15.0, # FIXME 13
    pull_up_l: 15.0,
    chin_up: 15.0, # FIXME 13
    dip    : 15.0, # FIXME 15?
    squat  : 38.0, # FIXME 90.0,
    # FIXME process historic stuff and make sure they are specified for both legs?
}
# then one rep is the inverse (with a multiplier to make numbers nicer)
one_rep: dict[str, float] = {
    k.kind: 15.0 / v
    for k, v in max_reps.items()
}
one_rep[squat_pistol.kind] = 1.0 # 15 for both legs total
one_rep[hollow_rock .kind] = 13.0 / 40
one_rep[squat_pistol.kind] = 1.0
one_rep[knee_raise  .kind] = 0.5
one_rep[calf_raise  .kind] = 0.2
one_rep[step_up     .kind] = 1.0
one_rep[hollow_leg_hold.kind] = 15.0 / 120 # 120 secs is pretty hard, comparable with say 15 pull ups?
one_rep[squat_hold  .kind] = 16.0 / 180
# TODO ok, calf raises and step ups are different. wtf it was???
# fmt: on


@lru_cache(None)
def vmap(x: SpecIsh) -> float | None:
    if isinstance(x, Spec):
        s = x.kind
    else:
        s = x
    return one_rep.get(s, None)


del S
