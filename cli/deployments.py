
import json

import click

from utils import parse_payload
from utils.context import get_cli_context
from craft_ai_sdk.constants import DEPLOYMENT_MODES

@click.group()
def deployments():
    """Manage deployments"""
    pass

@deployments.command()
@click.argument('name', required=True)
@click.argument('pipeline_name', required=True)
@click.option('--description', type=str, help="Pipeline description")
@click.option('--mode', type=click.Choice(['elastic', 'low-latency']), default='elastic')
@click.option('--rule', type=click.Choice(['periodic', 'endpoint']), default='endpoint')
@click.option('--schedule', type=str, help="Cron schedule for periodic type")
def create(name: str, pipeline_name: str, description: str | None, mode: str, rule: str, schedule: str | None):
    """Create a deployment"""
    ctx = get_cli_context()
    if rule == 'periodic' and not schedule:
        raise click.ClickException("Schedule is required for periodic rule")
    
    # Call SDK
    try:
        result = ctx.obj.sdk_instance.create_deployment(
            deployment_name=name,
            pipeline_name=pipeline_name,
            description=description,
            mode={'elastic': DEPLOYMENT_MODES.ELASTIC, 'low-latency': DEPLOYMENT_MODES.LOW_LATENCY, None: None}[mode],
            execution_rule=rule,
            schedule=schedule
        )
        click.echo(f"Deployment '{name}' created successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException(e) from e

@deployments.command()
@click.argument('name', required=True)
def get(name: str):
    """Get deployment details"""
    ctx = get_cli_context()
    
    # Call SDK
    try:
        result = ctx.obj.sdk_instance.get_deployment(name)
        click.echo(f"Deployment '{name}' retrieved successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException(e) from e

@deployments.command()
@click.argument('name', required=True)
def delete(name: str):
    """Delete a deployment"""
    ctx = get_cli_context()
    
    # Call SDK
    try:
        result = ctx.obj.sdk_instance.delete_deployment(name)
        click.echo(f"Deployment '{name}' deleted successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException(e) from e

@deployments.command()
@click.argument('name', required=True)
def logs(name: str):
    """Get the logs of a deployment"""
    ctx = get_cli_context()
    
    # Call SDK
    try:
        result = ctx.obj.sdk_instance.get_deployment_logs(name)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException(e) from e

@deployments.command()
@click.argument('name', required=True)
@click.option('--payload', type=str, help="Key-value dictionary with payload syntax. Run `<command> parse-payload` for help and testing")
def trigger(name: str, payload: str | None):
    """Trigger a deployment. Only valid for endpoint deployments"""
    ctx = get_cli_context()
    parsed_payload = None
    if payload:
        parsed_payload = parse_payload(payload)
        click.echo(f"Triggering deployment '{name}' with payload: {parsed_payload!r}")
    else:
        click.echo(f"Triggering deployment '{name}' with no payload")
    
    # Call SDK
    try:
        result = ctx.obj.sdk_instance.trigger_endpoint(name, inputs=parsed_payload)
        click.echo(f"Deployment '{name}' triggered successfully")
        click.echo(f'{result!r}')
    except Exception as e:
        raise click.ClickException(e) from e

