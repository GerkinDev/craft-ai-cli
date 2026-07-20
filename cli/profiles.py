from typing import List

import click
import json

from utils import tabulize, tabulize_list, tabulize_dict
from utils.context import (
    PROFILE_DIR,
    PROFILE_ENV_VAR,
    get_cli_context,
    resolve_profile_path,
)


def get_default_profile():
    if not DEFAULT_PROFILE_PATH.exists():
        return None

    with open(DEFAULT_PROFILE_PATH, "r") as f:
        default_profile = f.read().strip()
        resolve_profile_path(default_profile)
        return default_profile


def set_default_profile(name: str | None):
    if name is None:
        DEFAULT_PROFILE_PATH.unlink(True)
        return False

    resolve_profile_path(name)

    # Write default profile name
    with open(DEFAULT_PROFILE_PATH, "w") as f:
        f.write(name)
    return True


def ensure_profile_dir_exists():
    PROFILE_DIR.mkdir(exist_ok=True)


# Add this to the top of your module
DEFAULT_PROFILE_PATH = PROFILE_DIR / ".default_profile"


@click.group(name="profiles")
def profiles():
    """Manage profiles containing control/orchestrator/token configurations."""
    ensure_profile_dir_exists()


@profiles.command()
@click.argument("name", required=True)
@click.option("--control-url", required=False, help="Control service URL.")
@click.option("--orchestrator-url", required=True, help="Orchestrator service URL.")
@click.option(
    "--token",
    help="User token.",
    required=True,
    prompt="Enter your SDK token",
    prompt_required=False,
    hide_input=True,
)
@click.pass_context
def create(
    ctx: click.Context, name: str, control_url: str, orchestrator_url: str, token: str
):
    """Create a new profile with the specified settings."""

    if ctx.get_parameter_source("token") == click.ParameterSource.COMMANDLINE:
        click.echo(
            "Passing the token through commandline is insecure. Prefer using the `--token` flag without argument",
            err=True,
        )

    profile_path = resolve_profile_path(name, False)

    if profile_path.exists():
        click.confirm(f"Profile '{name}' already exists. Overwrite?", abort=True)

    profile_data = {
        "control_url": control_url,
        "orchestrator_url": orchestrator_url,
        "token": token,
    }

    with open(profile_path, "w") as f:
        json.dump(profile_data, f, indent=2)

    click.echo(f"Profile '{name}' created successfully.")


@profiles.command()
def list():
    """List all saved profiles in a table format with detailed information."""
    ctx = get_cli_context()
    profiles = [f.name for f in PROFILE_DIR.glob("*.json")]
    if not profiles:
        click.echo("No profiles found.")
        return

    # Get default profile
    default_profile = get_default_profile()

    # Collect all profile data
    profile_data_list: List[dict[str, str]] = []

    for profile in profiles:
        name = profile[:-5]  # Remove .json
        profile_path = resolve_profile_path(name)

        with open(profile_path, "r") as f:
            profile_raw_data = json.load(f)

        control_url = profile_raw_data.get("control_url", "N/A")
        orchestrator_url = profile_raw_data.get("orchestrator_url", "N/A")
        created_at = profile_raw_data.get("created_at", "N/A")
        is_default = name == default_profile
        is_active = name == ctx.obj.profile

        # build profile dict
        profile_dict: dict[str, str] = {
            "Name": name,
            "Control URL": control_url or "",
            "Orchestrator URL": orchestrator_url,
            "Created At": created_at,
            "Usage": ("★" if is_default else "  ") + ("🗹" if is_active else "   "),
        }
        profile_data_list.append(profile_dict)

    # Print table
    click.echo("Profiles:")
    click.echo(
        tabulize_list(
            profile_data_list, ["Name", "Usage", "Control URL", "Orchestrator URL"]
        )
    )


@profiles.command()
@click.argument("name", required=True)
@click.option("--control-url", help="New control service URL.")
@click.option("--orchestrator-url", help="New orchestrator service URL.")
@click.option(
    "--token",
    help="New user token.",
    prompt="Enter your SDK token",
    prompt_required=False,
    hide_input=True,
)
@click.pass_context
def update(
    ctx: click.Context,
    name: str,
    control_url: str | None,
    orchestrator_url: str | None,
    token: str | None,
):
    """Update an existing profile with new settings."""
    profile_path = resolve_profile_path(name)

    if ctx.get_parameter_source("token") == click.ParameterSource.COMMANDLINE:
        click.echo(
            "Passing the token through commandline is insecure. Prefer using the `--token` flag without argument",
            err=True,
        )

    with open(profile_path, "r") as f:
        profile_data = json.load(f)

    if control_url is not None:
        profile_data["control_url"] = control_url
    if orchestrator_url is not None:
        profile_data["orchestrator_url"] = orchestrator_url
    if token is not None:
        profile_data["token"] = token

    with open(profile_path, "w") as f:
        json.dump(profile_data, f, indent=2)

    click.echo(f"Profile '{name}' updated successfully.")


@profiles.command()
@click.argument("name", required=True)
def delete(name: str):
    """Delete an existing profile."""
    profile_path = resolve_profile_path(name)

    is_default = get_default_profile() == name
    profile_path.unlink()
    click.echo(f"Profile '{name}' deleted successfully.")
    if is_default:
        set_default_profile(None)
        click.echo("Default profile unset.")


@profiles.command()
@click.argument("name", required=False)
def set_default(name: str | None):
    """Set the default profile to use for commands."""

    if name:
        resolve_profile_path(name)

    if set_default_profile(name):
        click.echo(f"Default profile set to '{name}'.")
    else:
        click.echo("Default profile unset.")


@profiles.command()
def default():
    """Show the currently set default profile."""

    default_profile = get_default_profile()

    if default_profile is None:
        click.echo("No default profile set.")
        return

    click.echo(f"Current default profile: {default_profile}")


def _print_sourceable(values: dict[str, str | None]):
    click.echo(
        "\n".join(
            [
                f"export {key}='{value}'" if value else f"unset {key}"
                for (key, value) in values.items()
            ]
        )
    )


@profiles.command()
@click.argument("name", required=False)
@click.option(
    "--clear", is_flag=True, help="Unset the profile for the current session."
)
def use(name: str | None, clear: bool):
    """Show the command to export the given profile to the bash session.

    Example usage: `source <(craft-ai-cli profiles use <name>)`"""
    if clear:
        _print_sourceable({PROFILE_ENV_VAR: "_"})
        return
    if name is None:
        raise click.BadArgumentUsage("`<name> is required when `--clear` is not passed")

    resolve_profile_path(name)

    _print_sourceable({PROFILE_ENV_VAR: name})


@profiles.command()
@click.argument("name", required=False)
@click.option(
    "--clear", is_flag=True, help="Unset the profile for the current session."
)
@click.pass_context
def export(ctx: click.Context, name: str | None, clear: bool):
    """Show the command to export the given profile to the bash session.

    Example usage: `source <(craft-ai-cli profiles export)`"""
    if clear and name:
        raise click.exceptions.UsageError("Cannot use both `<name>` and `--clear`", ctx)
    if clear:
        fields: dict[str, str | None] = {
            PROFILE_ENV_VAR: None,
            "CRAFT_AI_SDK_TOKEN": None,
            "CRAFT_AI_ENVIRONMENT_URL": None,
            "CRAFT_AI_CONTROL_URL": None,
        }
        _print_sourceable(fields)
        return

    name_defaulted = name or get_default_profile()
    assert name_defaulted
    profile_path = resolve_profile_path(name_defaulted)

    with open(profile_path, "r") as f:
        profile_data = json.load(f)

    fields = {
        PROFILE_ENV_VAR: "_",
        "CRAFT_AI_SDK_TOKEN": profile_data["token"],
        "CRAFT_AI_ENVIRONMENT_URL": profile_data["orchestrator_url"],
        "CRAFT_AI_CONTROL_URL": profile_data.get("control_url", None),
    }
    _print_sourceable(fields)
