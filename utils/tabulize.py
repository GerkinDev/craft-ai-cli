import re


_ansi_re = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")

def strip_ansi(value: str) -> str:
    return _ansi_re.sub("", value)

def tabulize(columns: list[str | tuple[str, str]], data: list[dict[str, str]]):
    columns_normalized = dict(
        [(column, column) if isinstance(column, str) else column for column in columns]
    )
    min_widths = {
        key: len(label) for key, label in columns_normalized.items()
    }  # Minimum widths for each header
    for item in data:
        # update max lengths
        for key in columns_normalized.keys():
            column_value = item[key]
            min_widths[key] = max(min_widths[key], len(strip_ansi(column_value)))

    # Format headers with dynamic widths
    line_format = "{0}|{0}".join(
        [
            f"{{{index + 1}:<{min_widths[key]}}}"
            for (index, key) in enumerate(columns_normalized.keys())
        ]
    )

    return "\n".join(
        [
            line_format.format(" ", *[label for label in columns_normalized.values()]),
            line_format.format(
                "-", *["-" * min_widths[key] for key in columns_normalized.keys()]
            ),
            *[
                line_format.format(
                    " ", *[item[key] for key in columns_normalized.keys()]
                )
                for item in data
            ],
        ]
    )


def ellipsize(string: str, length: int):
    if len(string) > length:
        return string[0 : length - 1] + "…"
    return string
