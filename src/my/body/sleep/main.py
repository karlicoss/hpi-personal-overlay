from my.core import Stats, stat
from my.core.pandas import DataFrameT

from .common import Combine


def dataframe(*, with_temperature: bool = True) -> DataFrameT:
    from my.emfit import emfitexport
    from my.jawbone import api as jawbone

    return Combine([jawbone, emfitexport]).dataframe(with_temperature=with_temperature)


def stats() -> Stats:
    return stat(dataframe)
