import os
from pathlib import Path
import sys
from craft_ai_cli.cli.craft_ai_cli import cli


def generate_shell_integration(env_var_value: str, extension: str):
    target_file = (
        Path(__file__).parent
        / "../shell-integrations"
        / f"craft-ai-cli-complete{extension}"
    ).resolve()
    prev_argv = sys.argv
    prev_stdout = sys.stdout
    prev_sys_exit = sys.exit
    try:
        with open(target_file, "+wt") as f:
            sys.stdout = f
            sys.argv = ["craft-ai-cli"]
            os.environ["_CRAFT_AI_CLI_COMPLETE"] = env_var_value

            def hook_exit(*args, **kwargs):
                print(f"Hook exit {args=!r} {kwargs=!r}", file=sys.stderr)

            sys.exit = hook_exit
            cli()
            # subprocess.run(['craft-ai-cli'], env={'_CRAFT_AI_CLI_COMPLETE':env_var_value}, stdout=f)
    finally:
        sys.argv = prev_argv
        sys.stdout = prev_stdout
        sys.exit = prev_sys_exit


def generate_all_shell_integrations():
    generate_shell_integration("bash_source", ".bash")
    generate_shell_integration("zsh_source", ".zsh")
    generate_shell_integration("fish_source", ".fish")
    generate_shell_integration("powershell_source", ".ps1")


if __name__ == "__main__":
    generate_all_shell_integrations()
