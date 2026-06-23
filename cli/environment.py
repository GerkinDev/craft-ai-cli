import json

import click

from utils import CliContext, tabulize, ellipsize


@click.group()
def environment():
    """Manage environment"""
    pass

@environment.command()
@click.pass_context
def health(ctx: CliContext):
    health: dict[str, dict] = ctx.obj.sdk_instance._session.get(f'{ctx.obj.sdk_instance.base_environment_api_url}/health', verify=False).json()
    tab_items = [
        {
            'Name': key,
            'Status': entry['status'],
            'Details': ellipsize(json.dumps(entry.get('info', entry.get('error', None))), 50)
        } for (key, entry) in health.items()
    ]
    click.echo(tabulize(
        ['Name', 'Status', 'Details'],
        tab_items
    ))
