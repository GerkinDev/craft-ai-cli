from pprint import pformat, pprint

import click
from utils import parse_payload as parse, tabulize_dict
from utils.context import get_cli_context


@click.command()
@click.option(
    "--payload",
    type=str,
    required=True,
    help="Key-value dictionary with payload syntax. Run `<command> parse-payload` for help and testinng",
)
def parse_payload(payload: str):
    """Parse a payload for debugging purpose"""
    pprint(parse(payload))

@click.command()
def whoami():
    """Show current user info"""
    ctx = get_cli_context()

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.who_am_i()
        click.echo(tabulize_dict(result))
    except Exception as e:
        raise click.ClickException(e) from e
