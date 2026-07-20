
import click
from craft_ai_sdk.exceptions import SdkException
from craft_ai_sdk.io import Input, Output

from utils import get_cli_context, parse_payload, tabulize_dict, tabulize_list


@click.group()
def pipelines():
    """Manage pipelines"""
    pass


@pipelines.command()
@click.argument("name", required=True)
@click.option("--description", type=str, help="Pipeline description")
@click.option(
    "--function",
    type=str,
    help="Shorthand function syntax, in the form of <function-path>:<function-name>",
)
@click.option("--function-path", type=str, help="Path to the function file")
@click.option("--function-name", type=str, help="Name of the function in the file")
@click.option(
    "--language", type=str, help="Language and version (e.g., 'python:3.8-slim')"
)
@click.option(
    "--requirements-path", type=click.Path(), help="Path to requirements.txt file"
)
@click.option(
    "--included-folder",
    type=click.Path(),
    multiple=True,
    help="Add a folder/file to include (can be repeated)",
)
@click.option(
    "--system-dependency",
    type=str,
    multiple=True,
    help="Add a system dependency (can be repeated)",
)
@click.option("--dockerfile-path", type=click.Path(), help="Path to Dockerfile")
@click.option("--repository-url", type=str, help="Remote repository URL")
@click.option("--repository-branch", type=str, help="Branch name")
@click.option(
    "--repository-deploy-key", type=str, help="SSH private key for the repository"
)
@click.option(
    "--local-folder",
    type=click.Path(),
    help="Path to local folder containing the pipeline",
)
@click.option(
    "--inputs",
    type=str,
    help="Inputs with payload syntax in the form of `<name>=<config>,<name>=<config>`. Run `<command> parse-payload` for help and testing",
)
@click.option(
    "--outputs",
    type=str,
    help="Outputs with payload syntax in the form of `<name>=<config>,<name>=<config>`. Run `<command> parse-payload` for help and testing",
)
@click.option(
    "--recreate", is_flag=True, help="Recreate the pipeline if it already exists"
)
def create(
    name: str,
    description: str | None,
    function: str | None,
    function_path: str | None,
    function_name: str | None,
    language: str | None,
    requirements_path: str | None,
    included_folder: list[str] | None,
    system_dependency: list[str] | None,
    dockerfile_path: str | None,
    repository_url: str | None,
    repository_branch: str | None,
    repository_deploy_key: str | None,
    local_folder: str | None,
    inputs: str | None,
    outputs: str | None,
    recreate: bool,
):
    """Create a pipeline with full configuration"""
    ctx = get_cli_context()

    if recreate:
        try:
            ctx.obj.sdk_instance.delete_pipeline(name, True)
        except SdkException as e:
            if e.status_code != 404:
                raise

    if function:
        if function_path or function_name:
            raise click.ClickException(
                "`--function` cannot be used with `--function-path` nor `--function-name`"
            )
        splitted = function.split(":", 2)
        function_path = splitted[0]
        function_name = splitted[1]
    else:
        if not function_path or not function_name:
            raise click.ClickException(
                "You must provide either `--function-path` and `--function-name`, or `--function`"
            )

    # Parse inputs and outputs from JSON files
    parsed_inputs: list[Input] = []
    parsed_outputs: list[Output] = []

    if inputs:
        for input_name, input_config in parse_payload(inputs).items():
            parsed_inputs.append(Input(name=input_name, **input_config))

    if outputs:
        for output_name, output_config in parse_payload(outputs).items():
            parsed_outputs.append(Output(name=output_name, **output_config))

    # Build container config
    container_config = {
        "local_folder": local_folder,
        "repository_url": repository_url,
        "repository_branch": repository_branch,
        "repository_deploy_key": repository_deploy_key,
        "requirements_path": requirements_path,
        "included_folders": list(included_folder),
        "system_dependencies": list(system_dependency),
        "dockerfile_path": dockerfile_path,
        "language": language,
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
            wait_for_completion=True,
        )
        click.echo(f"Pipeline '{name}' created successfully")
        click.echo(tabulize_dict(result))
    except Exception as e:
        raise click.ClickException(e) from e


@pipelines.command()
@click.argument("name", required=True)
@click.option("--force-deployments-deletion")
def delete(name: str, force_deployments_deletion: bool):
    """Delete a pipeline"""
    ctx = get_cli_context()

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.delete_pipeline(
            name, force_deployments_deletion=force_deployments_deletion
        )
        click.echo(f"Pipeline '{name}' deleted successfully")
        click.echo(tabulize_dict(result))
    except Exception as e:
        raise click.ClickException(e) from e


@pipelines.command()
@click.argument("name", required=True)
def get(name: str):
    """Get pipeline details"""
    ctx = get_cli_context()

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.get_pipeline(name)
        click.echo(f"Pipeline '{name}' retrieved successfully")
        click.echo(tabulize_dict(result))
    except Exception as e:
        raise click.ClickException(e) from e


@pipelines.command("list")
def list_pipelines():
    """Get pipelines list"""
    ctx = get_cli_context()

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.list_pipelines()
        click.echo(tabulize_list(result))
    except Exception as e:
        raise click.ClickException(e) from e


@pipelines.command()
@click.argument("name", required=True)
@click.option(
    "--payload",
    type=str,
    help="Key-value dictionary with payload syntax. Run `<command> parse-payload` for help and testing",
)
def trigger(name: str, payload: str | None):
    """Trigger a pipeline"""
    ctx = get_cli_context()

    parsed_payload = None
    if payload:
        parsed_payload = parse_payload(payload)
        click.echo(f"Triggering pipeline '{name}' with payload: {parsed_payload!r}")
    else:
        click.echo(f"Triggering pipeline '{name}' with no payload")

    # Call SDK
    try:
        result = ctx.obj.sdk_instance.run_pipeline(name, parsed_payload)
        click.echo(f"Pipeline '{name}' retrieved successfully")
        click.echo(tabulize_dict(result))
    except Exception as e:
        raise click.ClickException(e) from e
