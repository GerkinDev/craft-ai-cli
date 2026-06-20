
import json

import click

from utils import CliContext

@click.group()
def executions():
    """Manage deployments"""
    pass

@executions.command()
@click.option('--deployment', type=str, help="Name of the deployment to get executions of")
@click.pass_context
def list(ctx: CliContext, deployment: str | None):
    """List executions with a given filter"""
    
    if deployment:
        pipeline_name = ctx.obj.sdk_instance.get_deployment(deployment)['pipeline']['name']

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.list_pipeline_executions(pipeline_name)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException("Failed") from e

