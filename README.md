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

## Full documentation

### craft-ai-cli [OPTIONS] COMMAND [ARGS]...

  Craft CLI - Pipeline and Deployment Management Tool

**Options:**

| Name                    | Description      |
|-------------------------|------------------|
| --control-url TEXT      | Control URL      |
| --orchestrator-url TEXT | Orchestrator URL |
| --token TEXT            | SDK token        |
| --profile TEXT          | Profile to use   |
| --no-profile            | Disable profile  |

**Commands:**

| Name          | Description                                                           |
|---------------|-----------------------------------------------------------------------|
| deployments   | Manage deployments                                                    |
| environment   | Manage environment                                                    |
| executions    | Manage executions                                                     |
| parse-payload | Parse a payload for debugging purpose                                 |
| pipelines     | Manage pipelines                                                      |
| profiles      | Manage profiles containing control/orchestrator/token configurations. |
| whoami        | Show current user info                                                |

---

#### craft-ai-cli pipelines [OPTIONS] COMMAND [ARGS]...

  Manage pipelines

**Commands:**

| Name    | Description                               |
|---------|-------------------------------------------|
| create  | Create a pipeline with full configuration |
| delete  | Delete a pipeline                         |
| get     | Get pipeline details                      |
| list    | Get pipelines list                        |
| logs    | Get the logs of a pipeline                |
| trigger | Trigger a pipeline                        |

---

##### craft-ai-cli pipelines create [OPTIONS] NAME

  Create a pipeline with full configuration

**Options:**

| Name                         | Description                                                                                                                      |
|------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| --description TEXT           | Pipeline description                                                                                                             |
| --function TEXT              | Shorthand function syntax, in the form of <function-path>:<function-name>                                                        |
| --function-path TEXT         | Path to the function file                                                                                                        |
| --function-name TEXT         | Name of the function in the file                                                                                                 |
| --language TEXT              | Language and version (e.g., 'python:3.8-slim')                                                                                   |
| --requirements-path PATH     | Path to requirements.txt file                                                                                                    |
| --included-folder PATH       | Add a folder/file to include (can be repeated)                                                                                   |
| --system-dependency TEXT     | Add a system dependency (can be repeated)                                                                                        |
| --dockerfile-path PATH       | Path to Dockerfile                                                                                                               |
| --repository-url TEXT        | Remote repository URL                                                                                                            |
| --repository-branch TEXT     | Branch name                                                                                                                      |
| --repository-deploy-key TEXT | SSH private key for the repository                                                                                               |
| --local-folder PATH          | Path to local folder containing the pipeline                                                                                     |
| --inputs TEXT                | Inputs with payload syntax in the form of `<name>=<config>,<name>=<config>`. Run `<command> parse-payload` for help and testing  |
| --outputs TEXT               | Outputs with payload syntax in the form of `<name>=<config>,<name>=<config>`. Run `<command> parse-payload` for help and testing |
| --recreate                   | Recreate the pipeline if it already exists                                                                                       |

---

##### craft-ai-cli pipelines delete [OPTIONS] NAME

  Delete a pipeline

**Options:**

| Name                              | Description |
|-----------------------------------|-------------|
| --force-deployments-deletion TEXT |             |

---

##### craft-ai-cli pipelines logs [OPTIONS] NAME

  Get the logs of a pipeline

---

##### craft-ai-cli pipelines get [OPTIONS] NAME

  Get pipeline details

---

##### craft-ai-cli pipelines list [OPTIONS]

  Get pipelines list

---

##### craft-ai-cli pipelines trigger [OPTIONS] NAME

  Trigger a pipeline

**Options:**

| Name           | Description                                                                                  |
|----------------|----------------------------------------------------------------------------------------------|
| --payload TEXT | Key-value dictionary with payload syntax. Run `<command> parse-payload` for help and testing |

---

#### craft-ai-cli deployments [OPTIONS] COMMAND [ARGS]...

  Manage deployments

**Commands:**

| Name                  | Description                  |
|-----------------------|------------------------------|
| create                | Create a deployment          |
| delete                | Delete a deployment          |
| get                   | Get deployment details       |
| list                  | List deployments             |
| logs                  | Get the logs of a deployment |
| rotate-endpoint-token | Update an endpoint token     |
| trigger               | Trigger a deployment.        |

---

##### craft-ai-cli deployments create [OPTIONS] NAME PIPELINE_NAME

  Create a deployment

**Options:**

| Name                              | Description                     |
|-----------------------------------|---------------------------------|
| --description TEXT                | Pipeline description            |
| --mode [elastic&#124;low-latency] |                                 |
| --rule [PERIODIC&#124;ENDPOINT]   |                                 |
| --schedule TEXT                   | Cron schedule for periodic type |

---

##### craft-ai-cli deployments get [OPTIONS] NAME

  Get deployment details

---

##### craft-ai-cli deployments delete [OPTIONS] NAME

  Delete a deployment

---

##### craft-ai-cli deployments logs [OPTIONS] NAME

  Get the logs of a deployment

---

##### craft-ai-cli deployments list [OPTIONS]

  List deployments

---

##### craft-ai-cli deployments rotate-endpoint-token [OPTIONS] NAME

  Update an endpoint token

**Options:**

| Name         | Description  |
|--------------|--------------|
| --token TEXT | Token to use |

---

##### craft-ai-cli deployments trigger [OPTIONS] NAME

  Trigger a deployment. Only valid for endpoint deployments

**Options:**

| Name           | Description                                                                                  |
|----------------|----------------------------------------------------------------------------------------------|
| --payload TEXT | Key-value dictionary with payload syntax. Run `<command> parse-payload` for help and testing |

---

#### craft-ai-cli executions [OPTIONS] COMMAND [ARGS]...

  Manage executions

**Commands:**

| Name | Description                         |
|------|-------------------------------------|
| get  | Get a single pipeline execution     |
| list | List executions with a given filter |

---

##### craft-ai-cli executions list [OPTIONS]

  List executions with a given filter

**Options:**

| Name              | Description                                 |
|-------------------|---------------------------------------------|
| --deployment TEXT | Name of the deployment to get executions of |
| --pipeline TEXT   | Name of the pipeline to get executions of   |

---

##### craft-ai-cli executions get [OPTIONS] EXECUTION_ID

  Get a single pipeline execution

---

#### craft-ai-cli profiles [OPTIONS] COMMAND [ARGS]...

  Manage profiles containing control/orchestrator/token configurations.

**Commands:**

| Name        | Description                                                          |
|-------------|----------------------------------------------------------------------|
| create      | Create a new profile with the specified settings.                    |
| default     | Show the currently set default profile.                              |
| delete      | Delete an existing profile.                                          |
| export      | Show the command to export the given profile to the bash session.    |
| list        | List all saved profiles in a table format with detailed information. |
| set-default | Set the default profile to use for commands.                         |
| update      | Update an existing profile with new settings.                        |
| use         | Show the command to export the given profile to the bash session.    |

---

##### craft-ai-cli profiles create [OPTIONS] NAME

  Create a new profile with the specified settings.

**Options:**

| Name                    | Description                           |
|-------------------------|---------------------------------------|
| --control-url TEXT      | Control service URL.                  |
| --orchestrator-url TEXT | Orchestrator service URL.  [required] |
| --token TEXT            | User token.  [required]               |

---

##### craft-ai-cli profiles list [OPTIONS]

  List all saved profiles in a table format with detailed information.

---

##### craft-ai-cli profiles update [OPTIONS] NAME

  Update an existing profile with new settings.

**Options:**

| Name                    | Description                   |
|-------------------------|-------------------------------|
| --control-url TEXT      | New control service URL.      |
| --orchestrator-url TEXT | New orchestrator service URL. |
| --token TEXT            | New user token.               |

---

##### craft-ai-cli profiles delete [OPTIONS] NAME

  Delete an existing profile.

---

##### craft-ai-cli profiles set-default [OPTIONS] [NAME]

  Set the default profile to use for commands.

---

##### craft-ai-cli profiles default [OPTIONS]

  Show the currently set default profile.

---

##### craft-ai-cli profiles use [OPTIONS] [NAME]

  Show the command to export the given profile to the bash session.

Example usage: `source <(craft-ai-cli profiles use <name>)`

**Options:**

| Name    | Description                                |
|---------|--------------------------------------------|
| --clear | Unset the profile for the current session. |

---

##### craft-ai-cli profiles export [OPTIONS] [NAME]

  Show the command to export the given profile to the bash session.

Example usage: `source <(craft-ai-cli profiles export)`

**Options:**

| Name    | Description                                |
|---------|--------------------------------------------|
| --clear | Unset the profile for the current session. |

---

#### craft-ai-cli environment [OPTIONS] COMMAND [ARGS]...

  Manage environment

**Commands:**

| Name   | Description                        |
|--------|------------------------------------|
| health | Get health of the environment      |
| info   | Get info of the environment        |
| put-on | Update the state of an environment |

---

##### craft-ai-cli environment health [OPTIONS]

  Get health of the environment

---

##### craft-ai-cli environment info [OPTIONS]

  Get info of the environment

---

##### craft-ai-cli environment put-on [OPTIONS] {ready|standby}

  Update the state of an environment

<target> is either ready or standby

**Options:**

| Name      | Description |
|-----------|-------------|
| --no-wait |             |

---

#### craft-ai-cli parse-payload [OPTIONS]

  Parse a payload for debugging purpose

**Options:**

| Name           | Description                                                                                               |
|----------------|-----------------------------------------------------------------------------------------------------------|
| --payload TEXT | Key-value dictionary with payload syntax. Run `<command> parse-payload` for help and testinng  [required] |

---

#### craft-ai-cli whoami [OPTIONS]

  Show current user info
