import json
import re
from typing import Any, Mapping, OrderedDict, Sequence


_ansi_re = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")


def strip_ansi(value: str) -> str:
    return _ansi_re.sub("", value)


def tabulize_list(
    data: Sequence[Mapping[str, Any]],
    columns: list[str | tuple[str, str]] | dict[str, str] | None = None,
):
    if columns is None:
        all_object_keys = list[str]()
        for item in data:
            all_object_keys.extend(item.keys())
        columns = {}
        all_object_keys = list(OrderedDict.fromkeys(all_object_keys))
        for object_key in all_object_keys:
            spaced_key = " ".join(object_key.split("_"))
            columns[object_key] = spaced_key[0].upper() + spaced_key[1:]
    return tabulize(columns, data)


def tabulize_dict(data: Mapping[str, Any]):
    return tabulize_list([{"Key": key, "Value": value} for key, value in data.items()], ["Key", "Value"])


def tabulize(
    columns: list[str | tuple[str, str]] | dict[str, str],
    data: Sequence[Mapping[str, Any]],
):
    columns_normalized = dict(
        [
            (column, column) if isinstance(column, str) else column
            for column in (columns if isinstance(columns, list) else columns.items())
        ]
    )
    return _tabulize(columns_normalized, data)


def _tabulize(columns: dict[str, str], data: Sequence[Mapping[str, Any]]):
    min_widths = {
        key: len(label) for key, label in columns.items()
    }  # Minimum widths for each header
    out_data: list[dict[str, str]] = []

    def serialize_data(value: Any):
        if isinstance(value, str):
            return value
        elif isinstance(value, bool):
            return "t" if value else "f"
        elif value is None:
            return ""
        elif isinstance(value, list) or isinstance(value, dict):
            return "$" + json.dumps(value)
        else:
            raise TypeError(f"Unexpected value of type {type(column_value)}")

    for item in data:
        out_data_item: dict[str, str] = {}
        # update max lengths
        for key in columns.keys():
            column_value = serialize_data(item[key])
            out_data_item[key] = column_value
            min_widths[key] = max(min_widths[key], len(strip_ansi(column_value)))
        out_data.append(out_data_item)

    # Format headers with dynamic widths
    line_format = "{0}|{0}".join(
        [
            f"{{{index + 1}:<{min_widths[key]}}}"
            for (index, key) in enumerate(columns.keys())
        ]
    )

    return "\n".join(
        [
            line_format.format(" ", *[label for label in columns.values()]),
            line_format.format("-", *["-" * min_widths[key] for key in columns.keys()]),
            *[
                line_format.format(" ", *[item[key] for key in columns.keys()])
                for item in out_data
            ],
        ]
    )


def ellipsize(string: str, length: int):
    if len(string) > length:
        return string[0 : length - 1] + "…"
    return string
