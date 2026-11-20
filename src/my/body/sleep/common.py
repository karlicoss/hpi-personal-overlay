"""Combine sleep trackers, room temperature and manual sleep notes."""

from datetime import timedelta

from my.core import Stats, stat
from my.core.pandas import DataFrameT, check_dataframe

from . import manual

_DELTA = timedelta(hours=20)


class Combine:
    def __init__(self, modules) -> None:
        self.modules = modules

    @check_dataframe
    def _tracker_dataframe(self, *, with_temperature: bool) -> DataFrameT:
        import pandas as pd

        # todo include 'source'?
        df = pd.concat([m.dataframe() for m in self.modules])

        if with_temperature:
            from ... import bluemaestro as BM

            bdf = BM.dataframe()
            temp = bdf['temp']

            # sort index and drop nans, otherwise indexing with [start: end] gonna complain
            temp = pd.Series(temp.values, index=pd.to_datetime(temp.index, utc=True)).sort_index()
            temp = temp.loc[temp.index.dropna()]

            def calc_avg_temperature(row):
                start = row['sleep_start']
                end   = row['sleep_end']  # fmt: skip
                if pd.isna(start) or pd.isna(end):
                    return None

                # on no temp data, returns nan, ok
                return temp[start:end].mean()

            df['avg_temp'] = df.apply(calc_avg_temperature, axis=1)
        return df

    def dataframe(self, *, with_temperature: bool = True) -> DataFrameT:
        odf = self._tracker_dataframe(with_temperature=with_temperature)
        mdf = manual.dataframe()

        # Keep manual errors in the result even when the tracker data has no matching row.
        # TODO implement a generic method, reuse in cross_trainer??
        import pandas as pd

        rows = []
        idxs = []  # type: ignore[var-annotated]
        for _i, row in mdf.iterrows():
            rd = row.to_dict()
            is_error = not pd.isna(rd['error'])
            if is_error:
                idxs.append(None)
                rows.append(rd)
                continue
            dt = rd['dt']
            # TODO not sure if need this in the resulting dataframe??
            close = odf[odf['sleep_end'].between(dt - _DELTA, dt)]
            if len(close) == 0:
                idx = None
                d = {
                    **rd,
                    'error': 'no sleep matches',
                }
            elif len(close) > 1:
                idx = None
                d = {
                    **rd,
                    'error': f'multiple sleeps matched: {close}',
                }
            else:
                idx = close.index[0]
                # TODO ok, in this case just need to attach?? not sure how..
                d = rd
                # TODO warn if already in index?
            idxs.append(idx)
            rows.append(d)

        df = pd.DataFrame(rows, index=idxs)
        rdf = odf.join(df, how='outer', rsuffix='_manual')

        def combine(l):
            l = [x for x in l if not pd.isna(x)]
            if len(l) == 0:
                return None
            else:
                return '; '.join(l)

        # TODO error_manual might not be present? not sure how to make defensive
        rdf['error'] = rdf[['error', 'error_manual']].agg(combine, axis=1)
        rdf = rdf.drop(columns=['error_manual'])
        # TODO need to test this stuff..
        # TODO for testing, check for presence of 'mental' or 'dreams' cols??
        return rdf

    def stats(self) -> Stats:
        return stat(self.dataframe)
