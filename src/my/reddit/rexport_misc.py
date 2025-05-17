### elaborate attempt of restoring favorite/unfavorite times
import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from datetime import datetime, timezone
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path
from typing import (
    NamedTuple,
    TypeAlias,
)

from my.core.utils.itertools import make_dict
from my.reddit import rexport as ORIG

##
logger = ORIG.logger
Uid: TypeAlias = ORIG.Uid
Save = ORIG.Save
inputs = ORIG.inputs
dal = ORIG.dal
##


# TODO hmm. apparently decompressing takes quite a bit of time...
class SaveWithDt(NamedTuple):
    save: ORIG.Save
    backup_dt: datetime

    def __getattr__(self, x):
        return getattr(self.save, x)


# TODO for future events?
EventKind = SaveWithDt


class Event(NamedTuple):
    dt: datetime
    text: str
    kind: EventKind
    eid: str
    title: str
    url: str

    @property
    def cmp_key(self):
        return (self.dt, (1 if 'unfavorited' in self.text else 0))


Url = str


def _get_bdate(bfile: Path) -> datetime:
    RE = re.compile(r'reddit.(\d{14})')
    stem = bfile.stem
    stem = stem.replace('T', '').replace('Z', '')  # adapt for arctee
    match = RE.search(stem)
    assert match is not None
    bdt = datetime.strptime(match.group(1), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    return bdt


def _get_state(bfile: Path) -> dict[Uid, SaveWithDt]:
    logger.debug('handling %s', bfile)

    bdt = _get_bdate(bfile)

    saves = [SaveWithDt(save, bdt) for save in dal.DAL([bfile]).saved()]
    return make_dict(
        sorted(saves, key=lambda p: p.save.created),
        key=lambda s: s.save.sid,
    )


# TODO hmm. think about it.. if we set default backups=inputs()
# it's called early so it ends up as a global variable that we can't monkey patch easily
# TODO ugh.. it was crashing for some reason??
# @mcachew(lambda backups: backups)
def _get_events(backups: Sequence[Path], *, parallel: bool = True) -> Iterator[Event]:
    # todo cachew: let it transform return type? so you don't have to write a wrapper for lists?

    prev_saves: Mapping[Uid, SaveWithDt] = {}
    # TODO suppress first batch??
    # TODO for initial batch, treat event time as creation time

    states: Iterable[Mapping[Uid, SaveWithDt]]
    if parallel:
        with Pool() as p:
            states = p.map(_get_state, backups)
    else:
        # also make it lazy...
        states = map(_get_state, backups)
    # TODO mm, need to make that iterative too?

    for i, (bfile, saves) in enumerate(zip(backups, states, strict=True)):
        bdt = _get_bdate(bfile)

        first = i == 0

        for key in set(prev_saves.keys()).symmetric_difference(set(saves.keys())):
            ps = prev_saves.get(key, None)
            if ps is not None:
                # TODO use backup date, that is more precise...
                # eh. I guess just take max and it will always be correct?
                assert not first
                yield Event(
                    dt=bdt,  # TODO average with ps.save_dt?
                    text="unfavorited",
                    kind=ps,
                    eid=f'unf-{ps.sid}',
                    url=ps.url,
                    title=ps.title,
                )
            else:  # already in saves
                s = saves[key]
                last_saved = s.backup_dt
                yield Event(
                    dt=s.created if first else last_saved,
                    text=f"favorited{' [initial]' if first else ''}",
                    kind=s,
                    eid=f'fav-{s.sid}',
                    url=s.url,
                    title=s.title,
                )
        prev_saves = saves

    # TODO a bit awkward, favorited should compare lower than unfavorited?

@lru_cache(1)
def events(*args, **kwargs) -> list[Event]:
    inp = inputs()
    # 2.2s for 300 files without cachew
    # 0.2s for 300 files with cachew
    evit = _get_events(inp, *args, **kwargs)
    # todo mypy is confused here and thinks it's iterable of Path? perhaps something to do with mcachew?
    return sorted(evit, key=lambda e: e.cmp_key)
