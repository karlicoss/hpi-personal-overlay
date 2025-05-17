from datetime import datetime, timezone
from pathlib import Path

import pytest

# deliberately use mixed style imports on the top level and inside the methods to test tmp_config stuff
import my.reddit.rexport_misc as my_reddit_rexport_misc
from my.core.cfg import tmp_config


# FIXME ugh... copypasted from main hpi...
# need to think how to discover testdata coming with the main package...
# perhaps could be a dependency somehow??
def hpi_repo_root() -> Path:
    root_dir = Path(__file__).absolute().parent.parent.parent.parent
    src_dir = root_dir / 'src'
    assert src_dir.exists(), src_dir
    return root_dir


def testdata() -> Path:
    d = hpi_repo_root() / 'testdata'
    assert d.exists(), d
    return d

# prevent pytest from treating this as test
testdata.__test__ = False  # type: ignore[attr-defined]



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
    assert len(favs) > 0
    [deal_with_it] = [f for f in favs if f.title == '"Deal with it!"']
    assert deal_with_it.backup_dt == datetime(2019, 4, 1, 23, 10, 25, tzinfo=timezone.utc)


def test_unfavorite() -> None:
    evs = my_reddit_rexport_misc.events()
    unfavs = [s for s in evs if s.text == 'unfavorited']
    assert len(unfavs) > 0
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
    # TODO maybe not relevant anymore?? ^^
    with tmp_config(modules='my.reddit.rexport.*', config=config):
        # sanity check to make sure it picked up test config
        assert 0 < len(my_reddit_rexport_misc.inputs()) < 10
        yield
