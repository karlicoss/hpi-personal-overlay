'''
Manually logged exercise from various sources (taplog/org-mode/etc)
'''
from typing import Dict, Iterable

from ...core.pandas import DataFrameT, check_dataframe as cdf, error_to_row
from .common import Exercise

from . import taplog


@cdf
def dataframe() -> DataFrameT:
    pre_df = (
        error_to_row(e) if isinstance(e, Exception) else e._asdict()
        for e in taplog.entries()
    )

    import pandas as pd # type: ignore
    return pd.DataFrame(pre_df)


from ...core import stat, Stats
def stats() -> Stats:
    return stat(dataframe)
