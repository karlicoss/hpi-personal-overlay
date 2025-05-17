'''
Overrides original common.py to attach manual sleep data
'''

from my.core.experimental import import_original_module

_ORIG = import_original_module(__name__, __file__, star=True, globals=globals())

from . import manual

orig = _ORIG.Combine.dataframe


def dataframe_override(self, *args, **kwargs):
    # call the original method first
    odf = orig(self, *args, **kwargs)

    # then compute the mixin data
    mdf = manual.dataframe()

    ## and now merge (needs a bit of elaborate logic to handle errors properly)
    # TODO implement a generic method, reuse in cross_trainer??
    import pandas as pd  # type: ignore[import-untyped]

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
    return rdf


_ORIG.Combine.dataframe = dataframe_override

####

from datetime import timedelta

_DELTA = timedelta(hours=20)


# TODO for testing, check for presence of 'mental' or 'dreams' cols??
