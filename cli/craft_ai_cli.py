import click
from craft_ai_sdk import CraftAiSdk

from cli.executions import executions
from cli.deployments import deployments
from cli.pipelines import pipelines
from cli.profiles import _get_default_profile, profiles
from cli.environment import environment
from utils import CliContext
from utils.context import CliContextObj

@click.group()
@click.option('--control-url', help="Control URL")
@click.option('--orchestrator-url', help="Orchestrator URL")
@click.option('--token', help="SDK token")
@click.option('--profile', help="Profile to use", default=_get_default_profile())
@click.option('--no-profile', help="Disable profile", is_flag=True)
@click.pass_context
def cli(ctx: CliContext, control_url: str | None, orchestrator_url: str | None, token: str | None, profile: str | None, no_profile: bool):
    """Craft CLI - Pipeline and Deployment Management Tool"""
    ctx.obj = CliContextObj(
        sdk_token=token, 
        orchestrator_url=orchestrator_url, 
        control_url=control_url,
        profile=None if no_profile else profile
    )
    pass


# Add commands to the CLI group
cli.add_command(pipelines)
cli.add_command(deployments)
cli.add_command(executions)
cli.add_command(profiles)
cli.add_command(environment)
