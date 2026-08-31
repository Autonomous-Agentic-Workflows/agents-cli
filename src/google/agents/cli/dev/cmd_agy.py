"""agents-cli agy command — Google Antigravity SDK integration."""

import subprocess
import os
import json
import urllib.request

import click

AGY_HOME = os.environ.get(
    "AGY_HOME",
    os.path.expanduser("~/antigravity-sdk-python-agent-workflow"),
)
AGY_VENV = os.path.join(AGY_HOME, ".venv")
AGY_PY = os.path.join(AGY_VENV, "bin", "python")
AGY_BRIDGE = os.path.join(
    AGY_HOME, "examples", "getting_started", "cross_agentic_bridge.py"
)
AGY_HARNESS = os.path.join(
    AGY_VENV,
    "lib",
    "python3.11",
    "site-packages",
    "google",
    "antigravity",
    "bin",
    "localharness",
)
VERTEX_ENV = os.path.expanduser("~/setup_enterprise_vertex_env.sh")
OLLAMA_API = "http://127.0.0.1:11434"


@click.group("agy", help="Commands for interacting with the Google Antigravity SDK.")
def agy():
    """Commands for interacting with the AGY (Antigravity) SDK.

    Provides an interface to launch the cross-agentic bridge, check
    installation status, install the SDK, and list available models.
    """


@agy.command("bridge", help="Launch the cross-agentic bridge.")
def bridge():
    """Launches the AGY cross-agentic bridge with Vertex AI + ollama fallback."""
    if not os.path.exists(AGY_BRIDGE):
        click.echo(f"Error: Bridge script not found at {AGY_BRIDGE}")
        click.echo("  Run 'agy install' first.")
        return
    if not os.path.exists(AGY_HARNESS):
        click.echo(f"Error: localharness binary not found at {AGY_HARNESS}")
        click.echo("  Run 'agy install' to install from PyPI.")
        return

    env = os.environ.copy()
    env["ANTIGRAVITY_HARNESS_PATH"] = AGY_HARNESS
    env["GOOGLE_CLOUD_PROJECT"] = os.environ.get(
        "GOOGLE_CLOUD_PROJECT", "master-recovery-hub-2026"
    )
    env["VERTEXAI_PROJECT"] = env["GOOGLE_CLOUD_PROJECT"]
    env["VERTEXAI_LOCATION"] = os.environ.get("VERTEXAI_LOCATION", "us-central1")

    # ADC credentials
    adc_candidates = [
        "/mnt/c/Users/jayla/AppData/Roaming/gcloud/application_default_credentials.json",
        os.path.expanduser("~/.config/gcloud/application_default_credentials.json"),
    ]
    for adc in adc_candidates:
        if os.path.exists(adc):
            env["GOOGLE_APPLICATION_CREDENTIALS"] = adc
            break

    # Safely load environment variables from Vertex env script if it exists
    if os.path.exists(VERTEX_ENV):
        try:
            with open(VERTEX_ENV, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("export "):
                        stripped = stripped[7:].strip()
                    if "=" in stripped and not stripped.startswith("#"):
                        key, val = stripped.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key:
                            env[key] = val
        except OSError:
            pass

    click.echo("Launching AGY bridge with gemini-2.5-flash...")
    click.echo(f"  Venv:    {AGY_VENV}")
    click.echo(f"  Harness: {AGY_HARNESS}")
    click.echo(f"  Project: {env['GOOGLE_CLOUD_PROJECT']}")
    click.echo("")

    subprocess.run([AGY_PY, AGY_BRIDGE], env=env)


@agy.command("status", help="Check AGY SDK installation status.")
def status():
    """Checks if AGY SDK is installed, localharness exists, and ollama is reachable."""
    click.echo("AGY SDK Status:")
    click.echo(f"  AGY Home:  {AGY_HOME}")

    venv_ok = os.path.exists(AGY_PY)
    click.echo(f"  Venv:      {'✓ OK' if venv_ok else '✗ MISSING'} ({AGY_VENV})")

    harness_ok = os.path.exists(AGY_HARNESS)
    click.echo(f"  Harness:   {'✓ OK' if harness_ok else '✗ MISSING'}")

    bridge_ok = os.path.exists(AGY_BRIDGE)
    click.echo(f"  Bridge:    {'✓ OK' if bridge_ok else '✗ MISSING'}")

    if venv_ok:
        try:
            r = subprocess.run(
                [AGY_PY, "-c",
                 "from google.antigravity import Agent; print('importable')"],
                capture_output=True, text=True, timeout=10,
            )
            click.echo(
                f"  SDK Import: {'✓ OK' if 'importable' in r.stdout else '✗ FAILED'}"
            )
            if r.stderr:
                for line in r.stderr.strip().splitlines()[:3]:
                    click.echo(f"              {line}")
        except Exception as e:
            click.echo(f"  SDK Import: ✗ ERROR ({e})")

    try:
        resp = urllib.request.urlopen(f"{OLLAMA_API}/api/version", timeout=5)
        ver = json.loads(resp.read()).get("version", "?")
        click.echo(f"  Ollama:    ✓ OK (v{ver})")
    except Exception:
        click.echo("  Ollama:    ✗ UNREACHABLE")


@agy.command("install", help="Install or repair the AGY SDK venv.")
def install():
    """Creates the AGY venv and installs google-antigravity from PyPI."""
    uv = os.path.expanduser("~/.hermes/bin/uv")
    if not os.path.exists(uv):
        # Fallback to system uv
        import shutil
        uv = shutil.which("uv")
        if not uv:
            click.echo("Error: uv not found. Install from https://docs.astral.sh/uv/")
            return

    if not os.path.exists(AGY_VENV):
        click.echo(f"Creating venv at {AGY_VENV}...")
        subprocess.run(
            [uv, "venv", AGY_VENV, "--python", "python3.11"],
            check=True,
        )

    click.echo("Installing google-antigravity from PyPI...")
    subprocess.run(
        [
            uv, "pip", "install",
            "--python", AGY_PY,
            "--reinstall",
            "google-antigravity==0.1.10",
            "protobuf>=7.35.1",
        ],
        check=True,
    )
    click.echo("")
    click.echo("Done. Run 'agy status' to verify.")


@agy.command("models", help="List available ollama models.")
def models():
    """Lists all available ollama models."""
    try:
        resp = urllib.request.urlopen(f"{OLLAMA_API}/api/tags", timeout=5)
        data = json.loads(resp.read())
        model_list = data.get("models", [])
        if not model_list:
            click.echo("No models found.")
            return
        click.echo(f"Available models ({len(model_list)}):")
        click.echo("")
        for m in model_list:
            name = m.get("name", "?")
            size = m.get("size", 0)
            size_gb = size / 1e9 if size > 1e6 else 0
            details = m.get("details", {})
            family = details.get("family", "?") or "?"
            param = details.get("parameter_size", "?") or "?"
            kind = "cloud" if m.get("remote_model") else "local"
            click.echo(
                f"  {name:<25} {param:<10} {family:<12} {kind:<6} {size_gb:.1f}GB"
            )
    except Exception as e:
        click.echo(f"Error reaching ollama: {e}")