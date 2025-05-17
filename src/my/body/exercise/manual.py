'''
Manually logged exercise from various sources (taplog/org-mode/etc)
'''
from datetime import timezone
from itertools import chain

from my.core import Stats, stat
from my.core.pandas import DataFrameT, check_dataframe, error_to_row

from . import orgmode, taplog


@check_dataframe
def dataframe() -> DataFrameT:
    pre_df = (
        error_to_row(e, tz=timezone.utc) if isinstance(e, Exception) else dict(volume=e.volume, **e._asdict())
        for e in chain(taplog.entries(), orgmode.entries())
    )

    import pandas as pd  # type: ignore[import-untyped]
    return pd.DataFrame(pre_df)


def stats() -> Stats:
    return stat(dataframe)
