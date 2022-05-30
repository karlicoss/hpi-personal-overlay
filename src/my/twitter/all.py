from typing import Iterator

from my.core import Res
from my.twitter import talon
from my.twitter.common import merge_tweets, Tweet

from my.orig.my.twitter import all as ORIG


# talon is higher quality? so goes first
def tweets() -> Iterator[Res[Tweet]]:
    # NOTE: merge_tweets is basically called twice here.. but maybe it's fine
    yield from merge_tweets(
        talon  .tweets(),
        ORIG.tweets(),
    )


def likes() -> Iterator[Res[Tweet]]:
    yield from merge_tweets(
        talon  .likes(),
        ORIG.likes(),
    )
