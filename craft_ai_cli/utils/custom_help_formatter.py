from contextlib import contextmanager
import sys
from typing import Any

import click
import collections.abc as cabc


def measure_table(rows: cabc.Iterable[tuple[str, str]]) -> tuple[int, ...]:
    widths: dict[int, int] = {}

    for row in rows:
        for idx, col in enumerate(row):
            widths[idx] = max(widths.get(idx, 0), term_len(col))

    return tuple(y for x, y in sorted(widths.items()))


def iter_rows(
    rows: cabc.Iterable[tuple[str, str]], col_count: int
) -> cabc.Iterator[tuple[str, ...]]:
    for row in rows:
        yield row + ("",) * (col_count - len(row))


def term_len(str: str):
    return len(str)


def wrap_text(text: str, *args: Any, initial_indent: str | None = None, **kwargs: Any):
    return (initial_indent or "") + text


class CustomHelpFormatter(click.HelpFormatter):
    """This class helps with formatting text-based help pages.  It's
    usually just needed for very special internal cases, but it's also
    exposed so that developers can write their own fancy outputs.

    At present, it always writes into memory.

    :param indent_increment: the additional increment for each level.
    :param width: the width for the text.  This defaults to the terminal
                  width clamped to a maximum of 78.
    """

    def __init__(
        self,
        heading_level: int = 1,
        width: int | None = None,
        max_width: int | None = None,
    ) -> None:
        super().__init__(2, sys.maxsize, sys.maxsize)
        self.heading_level = heading_level

    @property
    def base_heading(self):
        return "#" * self.heading_level

    def write(self, string: str) -> None:
        """Writes a unicode string into the internal buffer."""
        self.buffer.append(string)

    def indent(self) -> None:
        """Increases the indentation."""
        self.current_indent += self.indent_increment

    def dedent(self) -> None:
        """Decreases the indentation."""
        self.current_indent -= self.indent_increment

    def write_usage(self, prog: str, args: str = "", prefix: str | None = None) -> None:
        """Writes a usage line into the buffer.

        :param prog: the program name.
        :param args: whitespace separated list of arguments.
        :param prefix: The prefix for the first line. Defaults to
            ``"Usage: "``.
        """

        if prefix is None:
            prefix = self.base_heading + " "

        usage_prefix = f"{prefix:>{self.current_indent}}{prog} "
        text_width = self.width - self.current_indent

        if not args:
            # Without args, the prefix's trailing space and the wrap_text
            # call that would normally place args on the line are both
            # unnecessary. Emit just the prefix line.
            self.write(usage_prefix.rstrip(" "))
            self.write("\n")
            return

        if text_width >= (term_len(usage_prefix) + 20):
            # The arguments will fit to the right of the prefix.
            indent = " " * term_len(usage_prefix)
            self.write(
                wrap_text(
                    args,
                    text_width,
                    initial_indent=usage_prefix,
                    subsequent_indent=indent,
                )
            )
        else:
            # The prefix is too long, put the arguments on the next line.
            self.write(usage_prefix)
            self.write("\n")
            indent = " " * (max(self.current_indent, term_len(prefix)) + 4)
            self.write(
                wrap_text(
                    args, text_width, initial_indent=indent, subsequent_indent=indent
                )
            )

        self.write("\n")

    def write_heading(self, heading: str) -> None:
        """Writes a heading into the buffer."""
        self.write(f"**{heading}:**\n\n")

    def write_paragraph(self) -> None:
        """Writes a paragraph into the buffer."""
        if self.buffer:
            self.write("\n")

    def write_text(self, text: str) -> None:
        """Writes re-indented text into the buffer.  This rewraps and
        preserves paragraphs.
        """
        indent = " " * self.current_indent
        self.write(
            wrap_text(
                text,
                self.width,
                initial_indent=indent,
                subsequent_indent=indent,
                preserve_paragraphs=True,
            )
        )
        self.write("\n")

    def write_dl(
        self,
        rows: cabc.Sequence[tuple[str, str]],
        col_max: int = 30,
        col_spacing: int = 2,
    ) -> None:
        """Writes a definition list into the buffer.  This is how options
        and commands are usually formatted.

        :param rows: a list of two item tuples for the terms and values.
        :param col_max: the maximum width of the first column.
        :param col_spacing: the number of spaces between the first and
                            second column.
        """

        def sanitize_col(col: str):
            return col.replace("|", "&#124;").replace("\n", "<br/>")

        rows = [(sanitize_col(first), sanitize_col(second)) for first, second in rows]
        widths = measure_table(rows)
        if len(widths) != 2:
            raise TypeError("Expected two columns for definition list")

        first_col_header = "Name"
        second_col_header = "Description"
        first_col_width = max(widths[0], len(first_col_header))
        second_col_width = max(widths[1], len(second_col_header))
        line_format = f"|{{0}}{{1:<{first_col_width}}}{{0}}|{{0}}{{2:<{second_col_width}}}{{0}}|\n"

        self.write(line_format.format(" ", first_col_header, second_col_header))
        self.write(
            line_format.format("-", "-" * first_col_width, "-" * second_col_width)
        )
        for first, second in iter_rows(rows, len(widths)):
            self.write(line_format.format(" ", first, second))

    @contextmanager
    def section(self, name: str) -> cabc.Iterator[None]:
        """Helpful context manager that writes a paragraph, a heading,
        and the indents.

        :param name: the section name that is written as heading.
        """
        self.write_paragraph()
        self.write_heading(name)
        self.indent()
        try:
            yield
        finally:
            self.dedent()

    @contextmanager
    def indentation(self) -> cabc.Iterator[None]:
        """A context manager that increases the indentation."""
        self.indent()
        try:
            yield
        finally:
            self.dedent()

    def getvalue(self) -> str:
        """Returns the buffer contents."""
        return "".join(self.buffer)
