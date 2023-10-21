from typing import Iterator

from my.core import Res
from my.twitter import talon
from my.twitter.common import merge_tweets, Tweet

from my.core.experimental import import_original_module

_ORIG = import_original_module(__name__, __file__, star=True, globals=globals())


# talon is higher quality? so goes first
def tweets() -> Iterator[Res[Tweet]]:
    # NOTE: merge_tweets is basically called twice here.. but maybe it's fine
    yield from merge_tweets(
        talon.tweets(),
        _ORIG.tweets(),
    )


def likes() -> Iterator[Res[Tweet]]:
    yield from merge_tweets(
        talon.likes(),
        _ORIG.likes(),
    )
