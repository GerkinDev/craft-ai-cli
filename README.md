# Temp CLI wrapper for CraftAISdk

## Installation

1. Clone the repository
2. Install dependencies in <./requirements.txt>
3. Add the following to your `rc` file (`.bashrc`/`.zshrc`)

  ```sh
  export PATH="$PATH:<path to clone dir>/bin"
  ```

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
