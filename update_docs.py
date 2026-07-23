from pathlib import Path

import click

from craft_ai_cli.cli.craft_ai_cli import cli
from craft_ai_cli.utils.custom_help_formatter import CustomHelpFormatter


def recursive_help(
    cmd: click.Group, parent: click.Context | None = None, depth: int = 0
):
    ctx = click.core.Context(cmd, info_name=cmd.name, parent=parent)
    formatter = CustomHelpFormatter(depth + 1)
    cmd.add_help_option = False
    cmd.format_help(ctx, formatter)
    doc_page = formatter.getvalue().rstrip("\n") + "\n"
    yield doc_page
    commands = getattr(cmd, "commands", {})
    for sub in commands.values():
        for sub_help in recursive_help(sub, ctx, depth + 1):
            yield sub_help


root = Path(__file__).parent
with open(root / "README.md", "r") as f:
    readme = f.read()

DOCS_SECTION = "## Full documentation"
readme = readme.split(DOCS_SECTION)[0] + DOCS_SECTION + "\n\n"

readme = readme + "\n---\n\n".join(list(recursive_help(cli, None, 2)))

with open(root / "README.md", "w") as f:
    f.write(readme)
