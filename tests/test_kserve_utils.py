import numpy as np
import pandas as pd

from inferencedb.utils.kserve_utils import parse_kserve_request, parse_kserve_response, parse_kserve_v2_tensor


def test_pd_single_col_single_datapoint():
    result = parse_kserve_v2_tensor([
        {
            "name": "col1",
            "shape": [1],
            "datatype": "FP32",
            "data": [7.4],
        },
    ])

    expected = pd.DataFrame(data=[[7.4]], columns=["col1"])

    assert np.array_equal(result, expected)



def test_pd_single_col_multiple_datapoint():
    result = parse_kserve_v2_tensor([
        {
            "name": "col1",
            "shape": [3],
            "datatype": "FP32",
            "data": [7.4, 3.5, 7.8],
        },
    ])

    expected = pd.DataFrame(data=[
        [7.4],
        [3.5],
        [7.8],
    ], columns=["col1"])

    assert np.array_equal(result, expected)



def test_pd_multiple_col_single_datapoint():
    result = parse_kserve_v2_tensor([
        {
            "name": "col1",
            "shape": [1],
            "datatype": "FP32",
            "data": [3],
        },
        {
            "name": "col2",
            "shape": [1],
            "datatype": "FP32",
            "data": [4],
        },
    ])

    expected = pd.DataFrame(data=[
        [3, 4],
    ], columns=["col1", "col2"])

    assert np.array_equal(result, expected)


def test_pd_multiple_col_multiple_datapoints():
    result = parse_kserve_v2_tensor([
        {
            "name": "col1",
            "shape": [4],
            "datatype": "FP32",
            "data": [1, 2, 3, 4],
        },
        {
            "name": "col2",
            "shape": [4],
            "datatype": "FP32",
            "data": [5, 6, 7, 8],
        },
        {
            "name": "col3",
            "shape": [4],
            "datatype": "FP32",
            "data": [0, -1, -2, -3],
        },
    ])

    expected = pd.DataFrame(data=[
        [1, 5, 0],
        [2, 6, -1],
        [3, 7, -2],
        [4, 8, -3],
    ], columns=["col1", "col2", "col3"])

    assert np.array_equal(result, expected)


def test_np_multiple_col_multiple_datapoints():
    result = parse_kserve_v2_tensor([
        {
            "name": "input-0",
            "shape": [2, 4],
            "datatype": "FP32",
            "data": [
                [6.8, 2.8, 4.8, 1.4],
                [6.0, 3.4, 6.2, 1.8]
            ]
        }
    ])

    expected = pd.DataFrame(data=[
        [6.8, 2.8, 4.8, 1.4],
        [6.0, 3.4, 6.2, 1.8]
    ])

    assert np.array_equal(result, expected)


def test_pd_multiple_dtypes():
    result = parse_kserve_v2_tensor([
        {
            "name": "bool_column",
            "shape": [3],
            "datatype": "BOOL",
            "data": [True, True, False],
        },
        {
            "name": "float_column",
            "shape": [3],
            "datatype": "FP32",
            "data": [0.5, -4.6, 103.4],
        },
        {
            "name": "int_column",
            "shape": [3],
            "datatype": "INT32",
            "data": [32, 64, 128],
        },
        {
            "name": "string_column",
            "shape": [3],
            "datatype": "BYTES",
            "data": ["hello", "world", "!"],
        },
    ])

    expected = pd.DataFrame(data=[
        [True, 0.5, 32, "hello"],
        [True, -4.6, 64, "world"],
        [False, 103.4, 128, "!"],
    ], columns=["bool_column", "float_column", "int_column", "string_column"])

    assert result.equals(expected)
    assert result["bool_column"].dtype == "bool"
    assert result["float_column"].dtype == "float64"
    assert result["int_column"].dtype == "int64"
    assert result["string_column"].dtype == "object"


def test_text_and_embedding():
    result = parse_kserve_v2_tensor([
        {
            "name": "text",
            "shape": [2],
            "datatype": "BYTES",
            "data": ["Hello", "World"]
        },
        {
            "name": "embedding",
            "shape": [2, 4],
            "datatype": "FP32",
            "data": [
                [1, 2, 3, 4],
                [4, 5, 6, 7],
            ]
        }
    ])

    expected = pd.DataFrame(data=[
        ["Hello", [1, 2, 3, 4]],
        ["World", [4, 5, 6, 7]]
    ])

    assert np.array_equal(result, expected)


def test_kserve_v1_request():
    result = parse_kserve_request({
        "instances": [
            [1, 2, 3, 4],
            [4, 5, 6, 7],
        ]
    })

    expected = pd.DataFrame(data=[
        [1, 2, 3, 4],
        [4, 5, 6, 7],
    ])

    assert np.array_equal(result, expected)


def test_kserve_v1_response():
    result = parse_kserve_response({"predictions": [1, 1]})

    expected = pd.DataFrame(data=[
        [1],
        [1],
    ])

    assert np.array_equal(result, expected)


def test_kserve_v2_request():
    result = parse_kserve_request({
        "inputs": [
            {
                "name": "text",
                "shape": [2],
                "datatype": "BYTES",
                "data": ["Hello", "World"]
            },
            {
                "name": "embedding",
                "shape": [2, 4],
                "datatype": "FP32",
                "data": [
                    [1, 2, 3, 4],
                    [4, 5, 6, 7],
                ]
            }
        ]
    })

    expected = pd.DataFrame(data=[
        ["Hello", [1, 2, 3, 4]],
        ["World", [4, 5, 6, 7]]
    ])

    assert np.array_equal(result, expected)


def test_kserve_v2_response():
    result = parse_kserve_response({
        "outputs": [
            {
                "name": "predict",
                "shape": [3],
                "datatype": "FP32",
                "data": [2, 3, 4]
            }
        ]
    })

    expected = pd.DataFrame(data=[
        [2], [3], [4]
    ], columns=["predict"])

    assert np.array_equal(result, expected)
