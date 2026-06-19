
import json

import click

from utils.utils import CliContext, parse_payload

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
@click.pass_context
def create(ctx: CliContext, name: str, pipeline_name: str, description: str | None, mode: str, rule: str, schedule: str | None):
    """Create a deployment"""
    if rule == 'periodic' and not schedule:
        raise click.ClickException("Schedule is required for periodic rule")
    
    # Call SDK
    try:
        result = ctx.obj['sdk_instance'].create_deployment(deployment_name=name, pipeline_name=pipeline_name, description=description, mode=mode,execution_rule=rule, schedule=schedule)
        click.echo(f"Deployment '{name}' created successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException("Failed") from e

@deployments.command()
@click.argument('name', required=True)
@click.pass_context
def get(ctx: CliContext, name: str):
    """Get deployment details"""
    
    # Call SDK
    try:
        result = ctx.obj['sdk_instance'].get_deployment(name)
        click.echo(f"Deployment '{name}' retrieved successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException("Failed") from e

@deployments.command()
@click.argument('name', required=True)
@click.pass_context
def delete(ctx: CliContext, name: str):
    """Delete a deployment"""
    
    # Call SDK
    try:
        result = ctx.obj['sdk_instance'].delete_deployment(name)
        click.echo(f"Deployment '{name}' deleted successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException("Failed") from e

@deployments.command()
@click.argument('name', required=True)
@click.pass_context
def logs(ctx: CliContext, name: str):
    """Get the logs of a deployment"""
    
    # Call SDK
    result = ctx.obj['sdk_instance'].get_deployment_logs(name)
    click.echo(json.dumps(result, indent=2))

@deployments.command()
@click.argument('name', required=True)
@click.option('--payload', type=str, help="Key-value dictionary with special syntax")
@click.pass_context
def trigger(ctx: CliContext, name: str, payload: str | None):
    """Trigger a deployment. Only valid for endpoint deployments"""
    if payload:
        parsed_payload = parse_payload(payload)
        click.echo(f"Triggering deployment '{name}' with payload: {parsed_payload!r}")
    else:
        click.echo(f"Triggering deployment '{name}' with no payload")
    
    # Call SDK
    try:
        result = ctx.obj['sdk_instance'].trigger_endpoint(name)
        click.echo(f"Deployment '{name}' triggered successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException("Failed") from e

