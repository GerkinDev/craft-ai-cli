from pprint import pprint

import click
from utils import parse_payload as parse

@click.command()
@click.option('--payload', type=str, required=True, help="Key-value dictionary with payload syntax. Run `<command> parse-payload` for help and testinng")
def parse_payload(payload: str):
    """Parse a payload for debugging purpose"""
    pprint(parse(payload))
