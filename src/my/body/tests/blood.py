from datetime import datetime
from pathlib import Path

from my.core.cfg import tmp_config

from my.body.blood import Entry, data, dataframe


def test_blood_from_org_tables(tmp_path: Path) -> None:
    """Read a lab panel and a home measurement from the configured Org file in date order."""
    log = tmp_path / 'blood.org'
    log.write_text(
        '''\
* glucose/ketones
| datetime               | ket | glu | notes   |
|------------------------+-----+-----+---------|
| [2020-06-02 Tue 08:30] | 0.4 | 5.1 | morning |

* blood tests
| datetime               | VD nm/L | B12 pm/L | HDL mm/L | LDL mm/L | Trig mm/L | source | notes |
|------------------------+---------+----------+----------+----------+-----------+--------+-------|
| [2020-06-01 Mon 10:00] | 60      |          | 1.5      | 2.2 HI   | 0.9       | lab    | panel |
'''
    )

    class blood:
        @property
        def blood_log(self) -> Path:
            return log

    with tmp_config() as config:
        config.blood = blood
        expected = [
            Entry(
                dt=datetime(2020, 6, 1, 10),
                vitamin_d=60.0,
                hdl=1.5,
                ldl=2.2,
                triglycerides=0.9,
                source='lab',
                extra='panel',
            ),
            Entry(dt=datetime(2020, 6, 2, 8, 30), ketones=0.4, glucose=5.1, extra='morning'),
        ]
        assert list(data()) == expected
        assert dataframe()['dt'].tolist() == [entry.dt for entry in expected]
