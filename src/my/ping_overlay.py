from collections.abc import Iterable


def pong() -> Iterable[str]:
    yield from ['I', 'am', 'fine!']


def test_pong() -> None:
    assert ' '.join(pong()) == 'I am fine!'
