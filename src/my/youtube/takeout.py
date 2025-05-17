from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterator

from my.core import Res
from my.core.experimental import import_original_module

_ORIG = import_original_module(__name__, __file__, star=True, globals=globals())


_orig_watched = _ORIG._watched

# TODO import watched only for type checking? hmm
def _watched() -> Iterator[Res[Any]]:
    from my.time.tz.main import localize

    for w in _orig_watched():
        if isinstance(w, Exception):
            yield w
            continue

        # FIXME hmm... need to think how to do it in main module?
        # maybe some automatic wrapper for an iterator?
        when = localize(w.when, policy='convert')
        w = replace(w, when=when)
        yield w

_ORIG._watched = _watched  # type: ignore[attr-defined]
