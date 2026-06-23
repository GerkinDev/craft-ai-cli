from pprint import pprint


def tabulize(columns: list[str| tuple[str,str]], data: list[dict[str,str]]):
    columns_normalized = dict([
        (column,column) if isinstance(column, str) else column
        for column in columns
    ])
    min_widths = {key: len(label) for key, label in columns_normalized.items()}  # Minimum widths for each header
    pprint(min_widths)
    for item in data:
        # update max lengths
        for key in columns_normalized.keys():
            column_value = item[key]
            min_widths[key] = max(min_widths[key], len(column_value))

    # Format headers with dynamic widths
    header_format = ' | '.join([
        f"{{{index}:<{min_widths[key]}}}"
        for (index, key) in enumerate(columns_normalized.keys())
    ])
    separator = "-" * (sum(min_widths.values()) + (len(min_widths) - 1) * 3)

    return '\n'.join([
        header_format.format(*[label for label in columns_normalized.values()]),
        separator,
        *[header_format.format(*[item[key] for key in columns_normalized.keys()]) for item in data]
    ])

def ellipsize(string: str, length: int):
    if len(string) > length:
        return string[0:length-1] + "…"
    return string
