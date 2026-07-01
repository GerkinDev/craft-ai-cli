from datetime import datetime
import json
import time
from typing import Any, Literal, TypedDict, cast

import click
import requests

from utils import get_cli_context, tabulize, ellipsize


@click.group()
def environment():
    """Manage environment"""
    pass


def get_environment_summary():
    ctx = get_cli_context()
    summary: Any = ctx.obj.orchestrator.get("/api/v1/environment-summary").json()
    env_status = summary["environment_status"]
    env_update = datetime.fromisoformat(summary["environment_status_updated_at"])
    return EnvironmentSummary(status=env_status, updated_at=env_update)


class EnvironmentSummary(TypedDict):
    status: (
        Literal["creating-step-1"]
        | Literal["creating-step-2"]
        | Literal["creating-step-3"]
        | Literal["ready"]
        | Literal["pausing-step-1"]
        | Literal["pausing-step-2"]
        | Literal["standby"]
        | Literal["resuming-step-1"]
        | Literal["resuming-step-2"]
        | Literal["deleting-step-1"]
        | Literal["deleting-step-2"]
        | Literal["deleted"]
    )
    updated_at: datetime


@environment.command()
def health():
    """Get health of the environment"""
    ctx = get_cli_context()
    summary = get_environment_summary()
    health: dict[str, dict[str, Any]] = ctx.obj.orchestrator.anonymous.get(
        "/api/v1/health", raise_for_status=False
    ).json()  # type: ignore
    tab_items = [
        {
            "Name": "Environment status",
            "Status": summary["status"],
            "Details": str(summary["updated_at"]),
        },
        *[
            {
                "Name": key,
                "Status": cast(str, entry["status"]),
                "Details": ellipsize(
                    json.dumps(entry.get("info", entry.get("error", None))), 50
                ),
            }
            for (key, entry) in health.items()
        ],
    ]
    click.echo(tabulize(["Name", "Status", "Details"], tab_items))


@environment.command()
@click.argument("target", type=click.Choice(["ready", "standby"]))
@click.option("--no-wait", is_flag=True)
def put_on(target: str, no_wait: bool):
    """Update the state of an environment

    <target> is either ready or standby"""

    if target not in ["ready", "standby"]:
        raise click.BadArgumentUsage("`target` must be either `ready` or `standby`")

    ctx = get_cli_context()
    environment_summary = get_environment_summary()
    environment_status = environment_summary["status"]
    environment_id = ctx.obj.orchestrator.anonymous.get(
        "/api/v1/health", raise_for_status=False
    ).json()["environment_id"]["info"]
    if target == environment_status:
        click.echo("Environment is already in desired state")
        return
    if target == "ready":
        if environment_status.startswith("resuming-") or environment_status.startswith(
            "creating-"
        ):
            click.echo(
                f'Environment is in state {environment_status}, which is expected to transition to "ready"'
            )
        elif environment_status == "standby":
            click.echo("Sending request to environment")
            ctx.obj.control.patch(
                f"/api/v1/environments/{environment_id}", {"status": "resuming-step-1"}
            ).json()
        else:
            raise click.Abort(
                f"Environment is in unexpected state {environment_status}"
            )
    else:
        if environment_status.startswith("pausing-"):
            click.echo(
                f'Environment is in state {environment_status}, which is expected to transition to "standby"'
            )
        elif environment_status == "ready":
            click.echo("Sending request to environment")
            ctx.obj.control.patch(
                f"/api/v1/environments/{environment_id}", {"status": "pausing-step-1"}
            ).json()
        else:
            raise click.Abort(
                f"Environment is in unexpected state {environment_status}"
            )

    if no_wait:
        return

    click.echo(
        f"Waiting for the environment to transition to {target}. This may take a while"
    )
    tries = 0
    while environment_status != target:
        time.sleep(10)
        try:
            new_environment_status = get_environment_summary()["status"]
            if new_environment_status != environment_status:
                click.echo(f"Environment is now in state {new_environment_status}")
                environment_status = new_environment_status
        except requests.HTTPError as e:
            if tries > 10:
                raise e
            click.echo("Environment is not reachable, retry later")
            tries += 1
