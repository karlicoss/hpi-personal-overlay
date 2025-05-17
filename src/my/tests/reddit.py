from datetime import datetime, timezone

from my.core.cfg import tmp_config
from my.core.utils.itertools import make_dict

# todo ugh, it's discovered as a test???
from .common import testdata

import pytest

# deliberately use mixed style imports on the top level and inside the methods to test tmp_config stuff
import my.reddit.rexport as my_reddit_rexport
import my.reddit.rexport_misc as my_reddit_rexport_misc
import my.reddit.all as my_reddit_all


def test_events() -> None:
    from my.reddit.rexport_misc import events
    assert len(list(events())) > 0


def test_unfav() -> None:
    from my.reddit.rexport_misc import events

    ev = events()
    url = 'https://reddit.com/r/QuantifiedSelf/comments/acxy1v/personal_dashboard/'
    uev = [e for e in ev if e.url == url]
    assert len(uev) == 2
    ff = uev[0]
    # TODO could recover these from takeout perhaps?
    assert ff.text == 'favorited [initial]'
    uf = uev[1]
    assert uf.text == 'unfavorited'


def test_disappearing() -> None:
    # eh. so for instance, 'metro line colors' is missing from reddit-20190402005024.json for no reason
    # but I guess it was just a short glitch... so whatever
    evs = my_reddit_rexport_misc.events()
    favs = [s.kind for s in evs if s.text == 'favorited']
    [deal_with_it] = [f for f in favs if f.title == '"Deal with it!"']
    assert deal_with_it.backup_dt == datetime(2019, 4, 1, 23, 10, 25, tzinfo=timezone.utc)


def test_unfavorite() -> None:
    evs = my_reddit_rexport_misc.events()
    unfavs = [s for s in evs if s.text == 'unfavorited']
    [xxx] = [u for u in unfavs if u.eid == 'unf-19ifop']
    assert xxx.dt == datetime(2019, 1, 29, 10, 10, 20, tzinfo=timezone.utc)


@pytest.fixture(autouse=True, scope='module')
def prepare():
    data = testdata() / 'hpi-testdata' / 'reddit'
    assert data.exists(), data

    # note: deliberately using old config schema so we can test migrations
    class config:
        class reddit:
            export_dir = data
            please_keep_me = 'whatever'


    # NOTE ugh. need to .* prefix to account for my.orig.my.reddit... meh
    with tmp_config(modules='.*.my.reddit.rexport.*', config=config):
        assert len(my_reddit_rexport_misc.inputs()) < 10
        yield
