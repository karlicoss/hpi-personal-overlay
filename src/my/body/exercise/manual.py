'''
Manually logged exercise from various sources (taplog/org-mode/etc)
'''
from itertools import chain
from typing import Dict, Iterable

from ...core.pandas import DataFrameT, check_dataframe as cdf, error_to_row
from .common import Exercise

from . import taplog, orgmode


@cdf
def dataframe() -> DataFrameT:
    pre_df = (
        error_to_row(e) if isinstance(e, Exception) else dict(volume=e.volume, **e._asdict())
        for e in chain(taplog.entries(), orgmode.entries())
    )

    import pandas as pd # type: ignore
    return pd.DataFrame(pre_df)


from ...core import stat, Stats
def stats() -> Stats:
    return stat(dataframe)
