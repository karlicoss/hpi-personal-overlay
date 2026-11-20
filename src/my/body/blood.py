"""
Blood tracking (manual org-mode entries)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import orgparse
from my.core import Stats, stat
from my.core.error import Res, sort_res_by
from my.core.orgmode import one_table, parse_org_datetime
from my.core.pandas import DataFrameT


class Config(ABC):
    @property
    @abstractmethod
    def blood_log(self) -> Path | str:
        """Org file containing the glucose/ketones and blood tests tables."""
        raise NotImplementedError


def make_config() -> Config:
    from my.config import blood as user_config

    class combined_config(user_config, Config):
        pass

    return combined_config()


class Entry(NamedTuple):
    # fmt: off
    dt: datetime

    ketones      : float | None=None
    glucose      : float | None=None

    vitamin_d    : float | None=None
    vitamin_b12  : float | None=None

    hdl          : float | None=None
    ldl          : float | None=None
    triglycerides: float | None=None

    source       : str | None=None
    extra        : str | None=None
    # fmt: on


Result = Res[Entry]


def try_float(s: str) -> float | None:
    l = s.split()
    if len(l) == 0:
        return None
    # meh. this is to strip away HI/LO? Maybe need extract_float instead or something
    x = l[0].strip()
    if len(x) == 0:
        return None
    return float(x)


def glucose_ketones_data() -> Iterable[Result]:
    o = orgparse.load(make_config().blood_log)
    [n] = [x for x in o if x.heading == 'glucose/ketones']
    tbl = one_table(n)
    # todo some sort of sql-like interface for org tables might be ideal?
    for l in tbl.as_dicts:
        kets = l['ket']
        glus = l['glu']
        extra = l['notes']
        dt = parse_org_datetime(l['datetime'])
        try:
            assert isinstance(dt, datetime)
            ket = try_float(kets)
            glu = try_float(glus)
        except Exception as e:
            ex = RuntimeError(f'While parsing {l}')
            ex.__cause__ = e
            yield ex
        else:
            yield Entry(
                dt=dt,
                ketones=ket,
                glucose=glu,
                extra=extra,
            )


def blood_tests_data() -> Iterable[Result]:
    o = orgparse.load(make_config().blood_log)
    [n] = [x for x in o if x.heading == 'blood tests']
    tbl = one_table(n)
    for d in tbl.as_dicts:
        try:
            dt = parse_org_datetime(d['datetime'])
            assert isinstance(dt, datetime), dt

            F = lambda n: try_float(d[n])
            yield Entry(
                dt=dt,

                vitamin_d    =F('VD nm/L'),
                vitamin_b12  =F('B12 pm/L'),

                hdl          =F('HDL mm/L'),
                ldl          =F('LDL mm/L'),
                triglycerides=F('Trig mm/L'),

                source       =d['source'],
                extra        =d['notes'],
            )  # fmt: skip
        except Exception as e:
            ex = RuntimeError(f'While parsing {d}')
            ex.__cause__ = e
            yield ex


def data() -> Iterable[Result]:
    from itertools import chain

    datas = chain(glucose_ketones_data(), blood_tests_data())
    return sort_res_by(datas, key=lambda e: e.dt)


def dataframe() -> DataFrameT:
    import pandas as pd

    rows = []
    for x in data():
        if isinstance(x, Exception):
            # todo use some core helper? this is a pretty common operation
            d = {'error': str(x)}
        else:
            d = x._asdict()
        rows.append(d)
    return pd.DataFrame(rows)


def stats() -> Stats:
    return stat(data)
