from datetime import datetime
import json
import os
from pathlib import Path
from typing import Unpack, cast

import click
from craft_ai_sdk import CraftAiSdk
import requests._types as requests_types
import requests

PROFILE_DIR = Path.home() / ".config" / "craft-ai-cli"


def resolve_profile_path(profile_name: str, assert_exists: bool = True):
    path = PROFILE_DIR / f"{profile_name}.json"
    if assert_exists and not path.exists():
        raise click.ClickException(f"Profile '{profile_name}' does not exist.")
    return path


PROFILE_ENV_VAR = "CRAFT_AI_CLI_PROFILE"


class ExperimentalAuthentication(requests.auth.AuthBase):
    def __init__(self, cli_context: "CliContextObj"):
        self._cli_context = cli_context

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        sdk = self._cli_context.sdk_instance
        if sdk._access_token_data is None or (
            datetime.now() > sdk._access_token_valid_until - sdk._access_token_margin
        ):
            sdk._refresh_access_token()
        new_headers = {"Authorization": f"Bearer {sdk._access_token}"}
        r.headers.update(new_headers)

        def on_unauthorized(response: requests.Response, *args, **kwargs):
            if response.status_code == 401:
                sdk._clear_access_token()

        response_hooks = r.hooks.get("response", [])
        response_hooks.append(on_unauthorized)
        r.hooks["response"] = response_hooks
        return r


class HttpWrapper:
    def __init__(
        self,
        cli_context: "CliContextObj",
        base_url: str,
        extra_kwargs: requests_types.BaseRequestKwargs | None = None,
    ):
        self._cli_context = cli_context
        self._base_url = base_url
        self._extra_kwargs = extra_kwargs

    def get(
        self,
        url: requests_types.UriType,
        params: requests_types.ParamsType = None,
        *,
        raise_for_status: bool = True,
        **kwargs: Unpack[requests_types.GetKwargs],
    ) -> requests.Response:
        response = self._cli_context.sdk_instance._session.get(
            f"{self._base_url}{url}",
            params=params,
            **{**(self._extra_kwargs or {}), **kwargs},
        )
        if raise_for_status:
            response.raise_for_status()
        return response

    def patch(
        self,
        url: requests_types.UriType,
        data: requests_types.DataType = None,
        *,
        raise_for_status: bool = True,
        **kwargs: Unpack[requests_types.DataKwargs],
    ) -> requests.Response:
        response = self._cli_context.sdk_instance._session.patch(
            f"{self._base_url}{url}",
            data=data,
            **{**(self._extra_kwargs or {}), **kwargs},
        )
        if raise_for_status:
            response.raise_for_status()
        return response


class ServiceClient(HttpWrapper):
    def __init__(self, cli_context: "CliContextObj", base_url: str):
        super().__init__(
            cli_context,
            base_url,
            extra_kwargs={"auth": ExperimentalAuthentication(cli_context)},
        )
        self.anonymous = HttpWrapper(
            cli_context,
            base_url,
        )


class CliContextObj:
    _sdk_instance: CraftAiSdk | None

    def __init__(
        self,
        *,
        control_url: str | None,
        orchestrator_url: str | None,
        sdk_token: str | None,
        profile: str | None,
    ):
        self._control_url = control_url
        self._orchestrator_url = orchestrator_url
        self._sdk_token = sdk_token
        self.profile = profile
        self._sdk_instance = None
        self._orchestrator = None
        self._control = None
        if profile:
            if (
                os.environ.get("CRAFT_AI_SDK_TOKEN", None)
                or os.environ.get("CRAFT_AI_ENVIRONMENT_URL", None)
                or os.environ.get("CRAFT_AI_CONTROL_URL", None)
            ):
                click.echo(
                    "Mixing up profile and environment variables. This may cause issue. Review your environment variables and make sure all is consistent",
                    err=True,
                )
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
                self._sdk_instance = CraftAiSdk(
                    sdk_token=self._sdk_token,
                    environment_url=self._orchestrator_url,
                    control_url=self._control_url,
                    verbose_log=True,
                )
            return self._sdk_instance
        except ValueError as e:
            raise ValueError(
                f"Invalid SDK configuration. Verify your profile, pass configuration with appropriate flags, or check your environment variables. Inner reason:\n  {e}"
            ) from e

    @property
    def orchestrator(self):
        if self._orchestrator is None:
            self._orchestrator = ServiceClient(
                self, self.sdk_instance.base_environment_url
            )
        return self._orchestrator

    @property
    def control(self):
        if self._control is None:
            self._control = ServiceClient(self, self.sdk_instance.base_control_url)
        return self._control


class CliContext(click.Context):
    obj: CliContextObj


def get_cli_context(requires_obj: bool = True):
    context = click.get_current_context()
    if requires_obj:
        assert isinstance(context.obj, CliContextObj)
    return cast(CliContext, context)
