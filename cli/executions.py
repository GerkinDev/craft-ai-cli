import json
from pprint import pformat
import click

from utils import get_cli_context, tabulize_list, tabulize_dict


@click.group()
def executions():
    """Manage executions"""
    pass


@executions.command()
@click.option(
    "--deployment", type=str, help="Name of the deployment to get executions of"
)
@click.option(
    "--pipeline", type=str, help="Name of the pipeline to get executions of"
)
def list(deployment: str | None, pipeline: str | None):
    """List executions with a given filter"""
    ctx = get_cli_context()

    if deployment is not None and pipeline is not None:
        raise click.exceptions.UsageError(
            "Cannot use both `--deployment` and `--pipeline`", ctx
        )

    if deployment:
        pipeline_name = ctx.obj.sdk_instance.get_deployment(deployment)["pipeline"][
            "name"
        ]
    elif pipeline:
        pipeline_name = pipeline
    else:
        raise click.exceptions.UsageError(
            "Missing either `--deployment` or `--pipeline`", ctx
        )

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.list_pipeline_executions(pipeline_name)
        click.echo(tabulize_list(result))
    except Exception as e:
        raise click.ClickException(e) from e


@executions.command()
@click.argument("execution_id", required=True)
def get(execution_id: str):
    """Get a single pipeline execution"""
    ctx = get_cli_context()

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.get_pipeline_execution(execution_id)
        click.echo(tabulize_dict(result))
    except Exception as e:
        raise click.ClickException(e) from e
