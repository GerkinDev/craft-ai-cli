import json
import os
from typing import Any, TypedDict

import click
from craft_ai_sdk import CraftAiSdk

class CliContextObj(TypedDict):
    sdk_instance: CraftAiSdk
class CliContext(click.Context):
    obj: CliContextObj

def parse_payload(payload_str: str) -> dict[str, Any]:
    """Parse the special payload format into a dictionary"""
    payload = {}
    items = payload_str.split(',')
    
    for item in items:
        key, value = item.split('=', 1)
        key = key.strip()
        
        # Handle file references
        if value.startswith('@'):
            file_path = value[1:].strip()
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    payload[key] = f.read()
            else:
                raise click.ClickException(f"File not found: {file_path}")
        
        # Handle JSON
        elif value.startswith('{') and value.endswith('}'):
            try:
                payload[key] = json.loads(value)
            except json.JSONDecodeError:
                raise click.ClickException(f"Invalid JSON in payload: {value}")
        
        # Handle boolean
        elif value.lower() in ('true', 'false'):
            payload[key] = value.lower() == 'true'
        
        # Handle numbers
        elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            payload[key] = int(value)
        
        # Handle strings
        else:
            payload[key] = value.strip()
    
    return payload
