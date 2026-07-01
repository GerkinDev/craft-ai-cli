import os

import click

from cli.executions import executions
from cli.deployments import deployments
from cli.pipelines import pipelines
from cli.profiles import get_default_profile, profiles
from cli.environment import environment
from cli.misc import parse_payload
from utils import CliContextObj, get_cli_context
from utils.context import PROFILE_ENV_VAR

@click.group(name="craft-ai-cli")
@click.option('--control-url', help="Control URL")
@click.option('--orchestrator-url', help="Orchestrator URL")
@click.option('--token', help="SDK token")
@click.option('--profile', help="Profile to use", default=os.environ.get(PROFILE_ENV_VAR, get_default_profile()))
@click.option('--no-profile', help="Disable profile", is_flag=True)
def cli(control_url: str | None, orchestrator_url: str | None, token: str | None, profile: str | None, no_profile: bool):
    """Craft CLI - Pipeline and Deployment Management Tool"""
    ctx = get_cli_context(False)
    if ctx.get_parameter_source('profile') == click.ParameterSource.COMMANDLINE and no_profile:
        raise click.exceptions.UsageError("Cannot use both `--profile` and `--no-profile`", ctx)
    ctx.obj = CliContextObj(
        sdk_token=token, 
        orchestrator_url=orchestrator_url, 
        control_url=control_url,
        profile=None if no_profile else (profile if profile != '_' else None)
    )
    pass


# Add commands to the CLI group
cli.add_command(pipelines)
cli.add_command(deployments)
cli.add_command(executions)
cli.add_command(profiles)
cli.add_command(environment)
cli.add_command(parse_payload)
