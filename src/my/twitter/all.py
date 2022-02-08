from typing import Iterator
from ..core import Res
from .common import merge_tweets, Tweet

from my.orig.my.twitter import all as ORIG
from . import talon


def tweets() -> Iterator[Res[Tweet]]:
    yield from merge_tweets(
        ORIG.tweets(),
        talon  .tweets(),
    )


def likes() -> Iterator[Res[Tweet]]:
    yield from merge_tweets(
        ORIG.likes(),
        talon  .likes(),
    )
