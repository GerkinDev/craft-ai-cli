import click
from craft_ai_sdk import CraftAiSdk

from cli.executions import executions
from cli.deployments import deployments
from cli.pipelines import pipelines
from utils import CliContext

@click.group()
@click.option('--control-url', help="Control URL")
@click.option('--orchestrator-url', help="Orchestrator URL")
@click.option('--token', help="SDK token")
@click.pass_context
def cli(ctx: CliContext, control_url: str | None, orchestrator_url: str | None, token: str | None):
    """Craft CLI - Pipeline and Deployment Management Tool"""
    ctx.obj = {"sdk_instance": CraftAiSdk(sdk_token=token, environment_url=orchestrator_url, control_url=control_url, verbose_log=True)}
    pass


# Add commands to the CLI group
cli.add_command(pipelines)
cli.add_command(deployments)
cli.add_command(executions)
