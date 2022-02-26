from typing import Optional

import pandas as pd
import pyarrow as pa
from pyarrow.feather import read_feather, write_feather


def optional_join(df1: Optional[pd.DataFrame], df2: Optional[pd.DataFrame]) -> pd.DataFrame:
    if df1 is None:
        return df2
    
    if df2 is None:
        return None
    
    return df1.join(df2)


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
