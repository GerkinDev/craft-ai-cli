import json
from pathlib import Path
from typing import cast

import click
from craft_ai_sdk import CraftAiSdk

PROFILE_DIR = Path.home() / ".config" / "craft-ai-cli"
def resolve_profile_path(profile_name: str, assert_exists: bool = True):
    path = PROFILE_DIR / f"{profile_name}.json"
    if assert_exists and not path.exists():
        raise click.ClickException(f"Profile '{profile_name}' does not exist.")
    return path

class CliContextObj():
    _sdk_instance: CraftAiSdk | None

    def __init__(
        self,
        *,
        control_url: str | None, 
        orchestrator_url: str | None, 
        sdk_token: str | None, 
        profile: str | None
    ):
        self._control_url = control_url
        self._orchestrator_url = orchestrator_url
        self._sdk_token = sdk_token
        self._profile = profile
        self._sdk_instance = None
        if profile:
            with open(resolve_profile_path(profile), "r") as f:
                profile_data = json.load(f)
                if self._control_url is None:
                    self._control_url = profile_data["control_url"]
                if self._orchestrator_url is None:
                    self._orchestrator_url = profile_data["orchestrator_url"]
                if self._sdk_token is None:
                    self._sdk_token = profile_data["token"]
    
    @property
    def sdk_instance(self):
        try:
            if self._sdk_instance is None:
                self._sdk_instance = CraftAiSdk(sdk_token=self._sdk_token, environment_url=self._orchestrator_url, control_url=self._control_url, verbose_log=True)
            return self._sdk_instance
        except ValueError as e:
            raise ValueError(f'Invalid SDK configuration. Verify your profile, pass configuration with appropriate flags, or check your environment variables. Inner reason:\n  {e}') from e

class CliContext(click.Context):
    obj: CliContextObj

def get_cli_context(requires_obj: bool = True):
    context = click.get_current_context()
    if requires_obj:
        assert isinstance(context.obj, CliContextObj)
    return cast(CliContext, context)
