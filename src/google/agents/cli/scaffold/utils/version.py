# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Version checking utilities for the CLI."""

import logging
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PACKAGE_NAME = "google-agents-cli"
# The 0.0.0 sentinel used when a real version can't be determined — an
# uninstalled/dev checkout (get_current_version) or an unreachable PyPI
# (get_latest_version). Not a real release, so it can't be fetched from PyPI.
UNKNOWN_VERSION = "0.0.0"
_UPDATE_CHECK_INTERVAL = 12 * 60 * 60  # 12 hours in seconds
_UPDATE_CHECK_STAMP = Path.home() / ".agents" / ".acli_update_check"
_UPDATE_CHECK_LATEST_VERSION_FILE = Path.home() / ".agents" / ".acli_latest_version"


def _update_check_is_due() -> bool:
    """Return True if enough time has elapsed since the last check."""
    try:
        last = float(_UPDATE_CHECK_STAMP.read_text(encoding="utf-8").strip())
        return (time.time() - last) > _UPDATE_CHECK_INTERVAL
    except (OSError, ValueError):
        return True


def _record_update_check() -> None:
    """Write the current timestamp to the stamp file."""
    try:
        _UPDATE_CHECK_STAMP.parent.mkdir(parents=True, exist_ok=True)
        _UPDATE_CHECK_STAMP.write_text(str(time.time()), encoding="utf-8")
    except OSError:
        pass


def get_current_version() -> str:
    """Get the current installed version of the package."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        # Package isn't installed (editable / dev checkout).
        return UNKNOWN_VERSION


def agents_cli_version_pin() -> str:
    """Return the version suffix to pin `google-agents-cli` in generated projects.

    Renders to `@<version>` for released builds and to an empty string for the
    `0.0.0` unknown-version sentinel, so local renders against an uninstalled
    package leave the deploy steps using an unpinned `google-agents-cli`.
    """
    current_version = get_current_version()
    if current_version == UNKNOWN_VERSION:
        return ""
    return f"@{current_version}"


def get_cached_latest_version() -> str:
    """Get the latest version from the local cache file."""
    try:
        return _UPDATE_CHECK_LATEST_VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return UNKNOWN_VERSION


def get_latest_version() -> str:
    """Get the latest version available on PyPI."""
    try:
        # Lazy import requests to speed up CLI startup time
        import requests
        response = requests.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json", timeout=2)
        if response.status_code == 200:
            return response.json()["info"]["version"]
        return UNKNOWN_VERSION
    except Exception:
        return UNKNOWN_VERSION  # PyPI couldn't be reached


def check_for_updates() -> tuple[bool, str, str]:
    """Check if a newer version of the package is available.

    Returns:
        Tuple of (needs_update, current_version, latest_version)
    """
    # Lazy import packaging.version to speed up CLI startup time
    from packaging import version as pkg_version

    current = get_current_version()
    latest = get_cached_latest_version()
    if latest == UNKNOWN_VERSION:
        latest = get_latest_version()

    needs_update = pkg_version.parse(latest) > pkg_version.parse(current)

    return needs_update, current, latest


def _spawn_background_update_check() -> None:
    """Spawns a detached background python process to query PyPI and write to the cache and stamp files.

    This ensures that the update check is completely non-blocking and doesn't add any network I/O
    latency to the CLI startup.
    """
    import sys
    try:
        from google.agents.cli._runner import popen_resolved_detached
    except ImportError:
        logging.debug("Could not import popen_resolved_detached")
        return

    # Record the check before spawning to prevent concurrent overlapping background checks
    _record_update_check()

    # Minimal script using standard library urllib.request so it starts instantly without heavy imports
    script = (
        "import json, sys, time, urllib.request\n"
        "from pathlib import Path\n"
        "try:\n"
        "    req = urllib.request.Request(\n"
        "        'https://pypi.org/pypi/google-agents-cli/json',\n"
        "        headers={'User-Agent': 'google-agents-cli-updater'}\n"
        "    )\n"
        "    with urllib.request.urlopen(req, timeout=5) as r:\n"
        "        data = json.loads(r.read().decode('utf-8'))\n"
        "        latest = data['info']['version']\n"
        "    latest_file = Path(sys.argv[1])\n"
        "    latest_file.parent.mkdir(parents=True, exist_ok=True)\n"
        "    latest_file.write_text(latest, encoding='utf-8')\n"
        "    stamp_file = Path(sys.argv[2])\n"
        "    stamp_file.write_text(str(time.time()), encoding='utf-8')\n"
        "except Exception:\n"
        "    pass\n"
    )

    try:
        # Use sys.executable to run with the exact same Python interpreter as CLI
        popen_resolved_detached(
            [
                sys.executable,
                "-c",
                script,
                str(_UPDATE_CHECK_LATEST_VERSION_FILE),
                str(_UPDATE_CHECK_STAMP),
            ],
            resolve_executable=False,
        )
    except Exception as e:
        logging.debug(f"Failed to spawn background update check: {e}")


def display_update_message() -> None:
    """Check for updates and display a message if an update is available.

    This reads the latest version instantly from the local cache file, meaning it is non-blocking.
    If the update check interval has elapsed, it spawns a detached background process to query PyPI
    and refresh the cache file asynchronously.
    """
    try:
        current = get_current_version()
        latest = get_cached_latest_version()

        if latest != UNKNOWN_VERSION:
            from packaging import version as pkg_version
            try:
                if pkg_version.parse(latest) > pkg_version.parse(current):
                    # Lazy import Console to speed up CLI startup time
                    from rich.console import Console

                    console = Console()
                    console.print(
                        f"\n[yellow]⚠️  Update available: {current} → {latest}[/]",
                        highlight=False,
                    )
                    console.print(
                        f"[yellow]Run `uv tool upgrade {PACKAGE_NAME}` to update.[/]",
                        highlight=False,
                    )
                    console.print(
                        f"[dim]If you installed differently: pip install --upgrade {PACKAGE_NAME} | pipx upgrade {PACKAGE_NAME}[/]",
                        highlight=False,
                    )
            except Exception:
                pass

        if _update_check_is_due():
            _spawn_background_update_check()
    except Exception as e:
        # Don't let version checking errors affect the CLI
        logging.debug(f"Error checking for updates: {e}")
