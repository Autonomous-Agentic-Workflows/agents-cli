import click
import os
import subprocess
import sys
import socket # For checking Ollama reachability
import urllib.request # For calling Ollama API
import json # For parsing Ollama API response

# --- AGY SDK and Venv Path Definitions ---
AGY_SDK_ROOT = "/home/conor-ops/antigravity-sdk-python-agent-workflow"
AGY_VENV_PATH = os.path.join(AGY_SDK_ROOT, ".venv")
AGY_VENV_PYTHON = os.path.join(AGY_VENV_PATH, "bin", "python")
AGY_VENV_PIP = os.path.join(AGY_VENV_PATH, "bin", "pip")
AGY_LOCALHARNESS_PATH = "/home/conor-ops/antigravity-sdk-python-agent-workflow/.venv/lib/python3.11/site-packages/google/antigravity/bin/localharness"
UV_PATH = "/home/conor-ops/.hermes/bin/uv"
# --- End Path Definitions ---

@click.group(
    "agy",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    help="Commands for interacting with the AGY SDK."
)
def agy():
    """
    Commands for interacting with the AGY SDK.

    This command group provides an interface to various functionalities
    of the Antigravity (AGY) SDK, allowing you to manage and interact
    with AGY agents and services.
    """
    pass

@agy.command("deploy", help="Deploy an AGY agent.")
@click.argument("agent_name")
@click.option(
    "--env",
    "-e",
    multiple=True,
    help="Environment variables to set for the deployment (e.g., KEY=VALUE)."
)
def deploy(agent_name: str, env: list[str]):
    """
    Deploys an AGY agent using the AGY SDK.

    This command initiates the deployment process for a specified AGY agent.
    You can pass environment variables required for the deployment.
    """
    click.echo(f"Initiating AGY agent deployment for: {agent_name}")
    if env:
        click.echo(f"  with environment variables: {', '.join(env)}")
    click.echo("  (Integration with AGY SDK deployment logic goes here)")
    # Example:
    # from agy_sdk import deploy_agent
    # deploy_agent(agent_name, env_vars=dict(item.split('=', 1) for item in env))

@agy.command("run", help="Run an AGY agent locally.")
@click.argument("agent_name")
@click.option(
    "--port",
    "-p",
    type=int,
    default=8080,
    help="Port to run the local agent on."
)
def run(agent_name: str, port: int):
    """
    Runs an AGY agent locally using the AGY SDK.

    This command starts a local instance of the specified AGY agent,
    typically for development and testing purposes.
    """
    click.echo(f"Running AGY agent: {agent_name} locally on port {port}")
    click.echo("  (Integration with AGY SDK local run logic goes here)")
    # Example:
    # from agy_sdk import run_local_agent
    # run_local_agent(agent_name, port=port)

@agy.command("bridge", help="Launches the cross-agentic bridge.")
@click.option(
    "--model",
    "-m",
    default="gemini-2.5-flash",
    help="The model to use for the cross-agentic bridge (e.g., gemini-2.5-flash)."
)
def bridge(model: str):
    """
    Launches the cross-agentic bridge script using the AGY virtual environment.

    This command executes the Python script located at
    ~/antigravity-sdk-python-agent-workflow/examples/getting_started/cross_agentic_bridge.py
    within its dedicated virtual environment, setting ANTAGRAVITY_HARNESS_PATH and specifying the model.
    """
    script_path = os.path.join(
        AGY_SDK_ROOT, "examples/getting_started/cross_agentic_bridge.py"
    )
    venv_python_path = AGY_VENV_PYTHON
    localharness_path = AGY_LOCALHARNESS_PATH # Use the updated constant

    if not os.path.exists(script_path):
        click.echo(click.style(f"Error: Bridge script not found at '{script_path}'", fg="red"), err=True)
        return
    if not os.path.exists(venv_python_path):
        click.echo(click.style(f"Error: AGY venv Python not found at '{venv_python_path}'. "
                               "Please ensure the AGY venv is set up correctly.", fg="red"), err=True)
        return
    if not os.path.exists(localharness_path):
        click.echo(click.style(f"Error: localharness binary not found at '{localharness_path}'. "
                               "Cannot launch bridge without it.", fg="red"), err=True)
        return

    click.echo(f"Launching cross-agentic bridge using AGY venv: {venv_python_path}")
    click.echo(f"Script: {script_path}")
    click.echo(f"Setting ANTAGRAVITY_HARNESS_PATH='{localharness_path}'")
    click.echo(f"Setting GOOGLE_CLOUD_PROJECT='master-recovery-hub-2026'")
    click.echo(f"Setting VERTEXAI_LOCATION='us-central1'")
    click.echo(f"Setting GOOGLE_APPLICATION_CREDENTIALS='/mnt/c/Users/jayla/AppData/Roaming/gcloud/application_default_credentials.json'")
    click.echo(f"Using model: {model}")

    # Prepare environment variables
    modified_env = os.environ.copy()
    modified_env["ANTAGRAVITY_HARNESS_PATH"] = localharness_path
    modified_env["GOOGLE_CLOUD_PROJECT"] = "master-recovery-hub-2026"
    modified_env["VERTEXAI_LOCATION"] = "us-central1"
    modified_env["GOOGLE_APPLICATION_CREDENTIALS"] = "/mnt/c/Users/jayla/AppData/Roaming/gcloud/application_default_credentials.json"

    try:
        subprocess.run(
            [venv_python_path, script_path, "--model", model], # Pass --model argument
            check=True,
            capture_output=False, # Allow script output to stream directly
            env=modified_env # Pass the modified environment
        )
        click.echo(click.style("Cross-agentic bridge launched successfully.", fg="green"))
    except FileNotFoundError as e:
        click.echo(click.style(f"Error: Command or script not found. Details: {e}", fg="red"), err=True)
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"Error: Bridge script exited with an error (code {e.returncode}).", fg="red"), err=True)
        # If capture_output was True, you'd print e.stdout and e.stderr here
    except Exception as e:
        click.echo(click.style(f"An unexpected error occurred: {e}", fg="red"), err=True)

@agy.command("status", help="Checks the AGY SDK installation status.")
def status():
    """
    Checks the AGY SDK installation status, including venv, google-antigravity import,
    localharness binary, and Ollama reachability.
    """
    click.echo("--- Checking AGY SDK Status ---")

    # 1. Check if AGY Venv exists
    click.echo(f"\n1. Checking AGY virtual environment at '{AGY_VENV_PATH}'...")
    if os.path.isdir(AGY_VENV_PATH):
        click.echo(click.style(f"  ✅ AGY Venv directory found.", fg="green"))
    else:
        click.echo(click.style(f"  ❌ AGY Venv directory NOT found.", fg="red"))
        click.echo(click.style("     Run 'agents-cli agy install' to create it.", fg="yellow"))
        # If venv doesn't exist, other venv-dependent checks will fail, so we can skip them
        return

    # 2. Check if google-antigravity is importable in the venv
    click.echo(f"\n2. Checking if 'google-antigravity' is importable in AGY Venv...")
    if not os.path.exists(AGY_VENV_PYTHON):
        click.echo(click.style(f"  ❌ AGY Venv Python executable NOT found at '{AGY_VENV_PYTHON}'.", fg="red"))
        click.echo(click.style("     Venv might be corrupted or path is incorrect.", fg="yellow"))
    else:
        try:
            # Run a Python command within the venv to attempt import
            result = subprocess.run(
                [AGY_VENV_PYTHON, "-c", "import google.antigravity"],
                capture_output=True,
                text=True,
                check=False,
                env={"PATH": os.environ["PATH"]} # Ensure system PATH is available
            )
            if result.returncode == 0:
                click.echo(click.style(f"  ✅ 'google-antigravity' is importable in AGY Venv.", fg="green"))
            else:
                click.echo(click.style(f"  ❌ 'google-antigravity' NOT importable in AGY Venv.", fg="red"))
                click.echo(click.style(f"     Error: {result.stderr.strip()}", fg="red"))
                click.echo(click.style("     Run 'agents-cli agy install' to install/reinstall it.", fg="yellow"))
        except FileNotFoundError:
            click.echo(click.style(f"  ❌ AGY Venv Python executable not found at '{AGY_VENV_PYTHON}'.", fg="red"))
            click.echo(click.style("     Venv might be corrupted or path is incorrect.", fg="yellow"))
        except Exception as e:
            click.echo(click.style(f"  ❌ An unexpected error occurred during import check: {e}", fg="red"))

    # 3. Check if localharness binary exists
    click.echo(f"\n3. Checking for localharness binary at '{AGY_LOCALHARNESS_PATH}'...")
    if os.path.exists(AGY_LOCALHARNESS_PATH) and os.path.isfile(AGY_LOCALHARNESS_PATH):
        click.echo(click.style(f"  ✅ localharness binary found.", fg="green"))
    else:
        click.echo(click.style(f"  ❌ localharness binary NOT found.", fg="red"))
        click.echo(click.style("     Please ensure 'localharness' is built/placed correctly.", fg="yellow"))

    # 4. Check if Ollama is reachable at 127.0.0.1:11434
    click.echo(f"\n4. Checking Ollama reachability at '127.0.0.1:11434'...")
    ollama_host = "127.0.0.1"
    ollama_port = 11434
    try:
        with socket.create_connection((ollama_host, ollama_port), timeout=1) as sock:
            click.echo(click.style(f"  ✅ Ollama server is reachable at {ollama_host}:{ollama_port}.", fg="green"))
    except (socket.timeout, ConnectionRefusedError):
        click.echo(click.style(f"  ❌ Ollama server NOT reachable at {ollama_host}:{ollama_port}.", fg="red"))
        click.echo(click.style("     Please ensure Ollama is running.", fg="yellow"))
        click.echo(click.style("     Download Ollama from: https://ollama.com/", fg="yellow"))
    except Exception as e:
        click.echo(click.style(f"  ❌ An unexpected error occurred during Ollama check: {e}", fg="red"))

    click.echo("\n--- AGY SDK Status Check Complete ---")


@agy.command("install", help="Installs the google-antigravity package into a dedicated venv.")
def install():
    """
    Installs the google-antigravity package from PyPI into a dedicated virtual environment using uv.
    """
    click.echo("Initiating AGY SDK installation...")

    venv_path = AGY_VENV_PATH
    venv_python_path = AGY_VENV_PYTHON
    sdk_root_path = AGY_SDK_ROOT

    # Check if uv is available
    if not os.path.exists(UV_PATH):
        click.echo(click.style(f"Error: 'uv' binary not found at '{UV_PATH}'.", fg="red"), err=True)
        click.echo(click.style("  Please ensure 'uv' is installed and accessible at this path.", fg="yellow"), err=True)
        return

    # 1. Create virtual environment using uv
    click.echo(f"Creating virtual environment at: {venv_path} using uv...")
    try:
        # uv venv <venv_path> --python python3.11
        subprocess.run(
            [UV_PATH, "venv", venv_path, "--python", "python3.11"],
            check=True,
            capture_output=False # Allow uv output to stream directly
        )
        click.echo(click.style("Virtual environment created successfully.", fg="green"))
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"Error creating virtual environment with uv: {e}", fg="red"), err=True)
        return
    except Exception as e:
        click.echo(click.style(f"An unexpected error occurred during venv creation with uv: {e}", fg="red"), err=True)
        return

    # 2. Install google-antigravity package using uv pip install
    click.echo(f"Installing 'google-antigravity' and dependencies into venv: {venv_path} using uv...")
    try:
        # uv pip install --python <venv_python_path> -e <sdk_root>[dev] protobuf>=7.35.1
        subprocess.run(
            [
                UV_PATH, "pip", "install",
                "--python", venv_python_path,
                "-e", f"{sdk_root_path}[dev]",
                "protobuf>=7.35.1"
            ],
            check=True,
            capture_output=False # Allow uv pip output to stream directly
        )
        click.echo(click.style("'google-antigravity' and dependencies installed successfully.", fg="green"))
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"Error installing 'google-antigravity' with uv: {e}", fg="red"), err=True)
        # uv's output is already streamed, so no need to print e.stdout/stderr here unless capture_output was True
    except Exception as e:
        click.echo(click.style(f"An unexpected error occurred during package installation with uv: {e}", fg="red"), err=True)

@agy.command("models", help="Lists available Ollama models that can be used as fallback.")
def models():
    """
    Lists available Ollama models by querying the Ollama API.
    """
    click.echo("Listing available Ollama models from http://127.0.0.1:11434/api/tags...")
    ollama_api_url = "http://127.0.0.1:11434/api/tags"
    try:
        with urllib.request.urlopen(ollama_api_url, timeout=5) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                models = data.get("models", [])
                if models:
                    click.echo(click.style("Available Ollama models:", fg="green"))
                    for model_info in models:
                        model_name = model_info.get("model")
                        if model_name:
                            click.echo(f"- {model_name}")
                else:
                    click.echo(click.style("No Ollama models found.", fg="yellow"))
            else:
                click.echo(click.style(f"Error: Failed to fetch models from Ollama API. Status code: {response.getcode()}", fg="red"), err=True)
    except urllib.error.URLError as e:
        click.echo(click.style(f"Error: Could not connect to Ollama server at {ollama_api_url}.", fg="red"), err=True)
        click.echo(click.style("  Please ensure Ollama is running and accessible.", fg="yellow"), err=True)
        click.echo(click.style(f"  Details: {e.reason}", fg="red"), err=True)
    except json.JSONDecodeError:
        click.echo(click.style("Error: Failed to parse JSON response from Ollama API.", fg="red"), err=True)
    except Exception as e:
        click.echo(click.style(f"An unexpected error occurred: {e}", fg="red"), err=True)

