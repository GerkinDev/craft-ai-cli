# Temp CLI wrapper for CraftAISdk

## Installation

1. Clone the repository
2. Navigate to the cloned directory and install dependencies:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Add the following to your `rc` file (`.bashrc`/`.zshrc`)
   ```sh
   export PATH="$PATH:<path to clone dir>/bin"
   ```

> You can work on your custom SDK by replacing `craft_ai_sdk>=...` with `file://</path/to/your/sdk>` in <./requirements.txt>, and reinstalling

## Useful commands

### Manage profiles

```sh
# Create a profile "Hello"
craft-ai-cli profiles create hello --control-url=... --orchestrator-url=... # Token will be prompted via STDIN
# Set that profile as default
craft-ai-cli profiles set-default hello
# Export the default profile as environment variables
source <(craft-ai-cli profiles export)
env | grep CRAFT_AI
#CRAFT_AI_SDK_TOKEN=...
#CRAFT_AI_ENVIRONMENT_URL=...
#CRAFT_AI_CONTROL_URL=...
```

### Create a pipeline

```sh
craft-ai-cli pipelines create data-continuity --function data-continuity/entry.py:entry --local-folder pipelines --language python:3.14-slim --outputs='run_time={data_type: string}'
```

Inputs and outputs use the payload syntax. See below for examples and informations

## Payload syntax

The payload syntax is loosely inspired from a combination between yaml and curl. It is always a key=value object at its top level.

**Examples**

| Payload syntax | Json equivalent |
|----------------|-----------------|
| `foo=bar` | `{"foo": "bar"}` |
| `foo="bar"` | `{"foo": "bar"}` |
| `foo=42` | `{"foo": 42}` |
| `foo={hello: [world]}` | `{"foo": {"hello": ["world"]}}` |
| `a=1,b="some,value",c=true` | `{"a": 1, "b": "some,value", "c": true}` |

You can also use the `@<file>` to read a file and include its content as a value.
