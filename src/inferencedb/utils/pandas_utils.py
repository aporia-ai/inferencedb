from typing import Any, Optional

from faust.serializers import Codec
import pandas as pd
import pyarrow as pa
from pyarrow.feather import read_feather, write_feather


def serialize_dataframe(df: pd.DataFrame) -> Optional[bytes]:
    if df is None:
        return None

    with pa.BufferOutputStream() as output_stream:
        write_feather(df, output_stream)
        return output_stream.getvalue().to_pybytes()


def deserialize_dataframe(data: Optional[bytes]) -> pd.DataFrame:
    if data is None:
        return None

    with pa.BufferReader(data) as reader:
        return read_feather(reader)
