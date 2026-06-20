
import json

import click

from utils import CliContext, parse_payload

@click.group()
def pipelines():
    """Manage pipelines"""
    pass

@pipelines.command()
@click.argument('name', required=True)
@click.option('--description', type=str, help="Pipeline description")
@click.option('--function-path', type=str, required=True, help="Path to the function file")
@click.option('--function-name', type=str, required=True, help="Name of the function in the file")
@click.option('--language', type=str, help="Language and version (e.g., 'python:3.8-slim')")
@click.option('--requirements-path', type=click.Path(), help="Path to requirements.txt file")
@click.option('--included-folders', multiple=True, help="List of folders/files to include (can be repeated)")
@click.option('--system-dependencies', multiple=True, help="List of system dependencies (can be repeated)")
@click.option('--dockerfile-path', type=click.Path(), help="Path to Dockerfile")
@click.option('--repository-url', type=str, help="Remote repository URL")
@click.option('--repository-branch', type=str, help="Branch name")
@click.option('--repository-deploy-key', type=str, help="SSH private key for the repository")
@click.option('--local-folder', type=click.Path(), help="Path to local folder containing the pipeline")
@click.option('--inputs', type=click.File('r'), help="Path to JSON file containing input definitions")
@click.option('--outputs', type=click.File('r'), help="Path to JSON file containing output definitions")
@click.pass_context
def create(
    ctx: CliContext,
    name: str,
    description: str | None,
    function_path: str,
    function_name: str,
    language: str | None,
    requirements_path: str | None,
    included_folders: list[str] | None,
    system_dependencies: list[str] | None,
    dockerfile_path: str | None,
    repository_url: str | None,
    repository_branch: str | None,
    repository_deploy_key: str | None,
    local_folder: str | None,
    inputs: click.File | None,
    outputs: click.File | None,
):
    """Create a pipeline with full configuration"""

    # Parse inputs and outputs from JSON files
    parsed_inputs = []
    parsed_outputs = []

    if inputs:
        try:
            parsed_inputs = json.load(inputs)
        except json.JSONDecodeError:
            raise click.ClickException("Invalid JSON in inputs file")

    if outputs:
        try:
            parsed_outputs = json.load(outputs)
        except json.JSONDecodeError:
            raise click.ClickException("Invalid JSON in outputs file")

    # Build container config
    container_config = {
        "local_folder": local_folder,
        "repository_url": repository_url,
        "repository_branch": repository_branch,
        "repository_deploy_key": repository_deploy_key,
        "requirements_path": requirements_path,
        "included_folders": list(included_folders) if included_folders else None,
        "system_dependencies": list(system_dependencies) if system_dependencies else None,
        "dockerfile_path": dockerfile_path,
        "language": language
    }

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.create_pipeline(
            pipeline_name=name,
            function_path=function_path,
            function_name=function_name,
            description=description,
            container_config=container_config,
            inputs=parsed_inputs,
            outputs=parsed_outputs,
            wait_for_completion=True
        )
        click.echo(f"Pipeline '{name}' created successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException(e) from e

@pipelines.command()
@click.argument('name', required=True)
@click.option('--force-deployments-deletion')
@click.pass_context
def delete(ctx: CliContext, name: str, force_deployments_deletion: bool):
    """Delete a pipeline"""

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.delete_pipeline(name,force_deployments_deletion=force_deployments_deletion)
        click.echo(f"Pipeline '{name}' deleted successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException(e) from e

@pipelines.command()
@click.argument('name', required=True)
@click.pass_context
def get(ctx: CliContext, name: str):
    """Get pipeline details"""

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.get_pipeline(name)
        click.echo(f"Pipeline '{name}' retrieved successfully")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        raise click.ClickException(e) from e

@pipelines.command()
@click.argument('name', required=True)
@click.option('--payload', type=str, help="Key-value dictionary with special syntax")
@click.pass_context
def trigger(ctx: CliContext, name: str, payload: str | None):
    """Trigger a pipeline"""
    
    if payload:
        parsed_payload = parse_payload(payload)
        click.echo(f"Triggering pipeline '{name}' with payload: {parsed_payload!r}")
    else:
        click.echo(f"Triggering pipeline '{name}' with no payload")
    raise click.Abort('Not implemented')
