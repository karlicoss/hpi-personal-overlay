from collections.abc import Iterator

from my.core.experimental import import_original_module

_ORIG = import_original_module(__name__, __file__, star=True, globals=globals())


def items() -> Iterator:
    yield from _ORIG.items()
    yield _ORIG.Item(dt=_ORIG.NOW, message='hpi overlay', path=_ORIG.get_pkg_path())
