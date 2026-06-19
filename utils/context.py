from typing import TypedDict

import click
from craft_ai_sdk import CraftAiSdk

class CliContextObj(TypedDict):
    sdk_instance: CraftAiSdk
class CliContext(click.Context):
    obj: CliContextObj
