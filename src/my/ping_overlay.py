from collections.abc import Iterable


def pong() -> Iterable[str]:
    yield from ['I', 'am', 'fine!']
