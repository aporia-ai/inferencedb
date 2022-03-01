from typing import List

import pandas as pd


def parse_kserve_v2_tensor(columns: List[dict]) -> pd.DataFrame:
    # If there's one column with a 2D shape, then we'll assume the first dimension
    # is the amount of rows, and the second dimension is the amount of columns.
    if len(columns) == 1 and len(columns[0]["shape"]) == 2:
        return pd.DataFrame(data=columns[0]["data"])

    return pd.DataFrame.from_dict({
        col["name"]: col["data"]
        for col in columns
    })



def parse_kserve_request(request: dict) -> pd.DataFrame:
    if "instances" in request:
        return pd.DataFrame(data=request["instances"])
    elif "inputs" in request:
        return parse_kserve_v2_tensor(request["inputs"])
    else:
        raise ValueError(f"Invalid KServe request: no 'instances' or 'inputs' fields")



def parse_kserve_response(response: dict) -> pd.DataFrame:
    if "predictions" in response:
        return pd.DataFrame(data=response["predictions"])
    elif "outputs" in response:
        return parse_kserve_v2_tensor(response["outputs"])
    else:
        raise ValueError(f"Invalid KServe response: no 'predictions' or 'outputs' fields")
