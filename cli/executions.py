import json
from pprint import pformat
import click

from utils import get_cli_context


@click.group()
def executions():
    """Manage executions"""
    pass


@executions.command()
@click.option(
    "--deployment", type=str, help="Name of the deployment to get executions of"
)
def list(deployment: str | None):
    """List executions with a given filter"""
    ctx = get_cli_context()

    if deployment:
        pipeline_name = ctx.obj.sdk_instance.get_deployment(deployment)["pipeline"][
            "name"
        ]

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.list_pipeline_executions(pipeline_name)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException(e) from e


@executions.command()
@click.argument("execution_id", required=True)
def get(execution_id: str):
    """List executions with a given filter"""
    ctx = get_cli_context()

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.get_pipeline_execution(execution_id)
        click.echo(pformat(result, indent=2))
    except Exception as e:
        raise click.ClickException(e) from e
