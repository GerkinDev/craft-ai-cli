import json
from typing import Any, cast

import click

from utils import get_cli_context, tabulize, ellipsize


@click.group()
def environment():
    """Manage environment"""
    pass

@environment.command()
def health():
    """Get health of the environment"""
    ctx = get_cli_context()
    health: dict[str, dict[str, Any]] = ctx.obj.sdk_instance._session.get(f'{ctx.obj.sdk_instance.base_environment_api_url}/health', verify=False).json() # type: ignore
    tab_items = [
        {
            'Name': key,
            'Status': cast(str, entry['status']),
            'Details': ellipsize(json.dumps(entry.get('info', entry.get('error', None))), 50)
        } for (key, entry) in health.items()
    ]
    click.echo(tabulize(
        ['Name', 'Status', 'Details'],
        tab_items
    ))
