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
_LATEST_VERSION_CACHE = Path.home() / ".agents" / ".acli_latest_version"


def _update_check_is_due() -> bool:
    """Return True if enough time has elapsed since the last check."""
    try:
        last = float(_UPDATE_CHECK_STAMP.read_text().strip())
        return (time.time() - last) > _UPDATE_CHECK_INTERVAL
    except (OSError, ValueError):
        return True


def _record_update_check() -> None:
    """Write the current timestamp to the stamp file."""
    try:
        _UPDATE_CHECK_STAMP.parent.mkdir(parents=True, exist_ok=True)
        _UPDATE_CHECK_STAMP.write_text(str(time.time()))
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
    latest = get_latest_version()

    needs_update = pkg_version.parse(latest) > pkg_version.parse(current)

    return needs_update, current, latest


def display_update_message() -> None:
    """Check for updates using cached version and spawn background check if due."""
    try:
        current = get_current_version()
        if current == UNKNOWN_VERSION:
            # Skip checking if we are running from a local/dev checkout.
            return

        # 1. Read latest known version from cache file instantly
        cached_latest = None
        if _LATEST_VERSION_CACHE.exists():
            try:
                cached_latest = _LATEST_VERSION_CACHE.read_text(encoding="utf-8").strip()
            except OSError:
                pass

        # 2. Compare versions if we have a valid cached version
        if cached_latest and cached_latest != UNKNOWN_VERSION:
            # Lazy import packaging.version to speed up CLI startup time
            from packaging import version as pkg_version

            try:
                needs_update = pkg_version.parse(cached_latest) > pkg_version.parse(current)
            except Exception:
                needs_update = False

            if needs_update:
                # Lazy import Console to speed up CLI startup time
                from rich.console import Console

                console = Console()
                console.print(
                    f"\n[yellow]⚠️  Update available: {current} → {cached_latest}[/]",
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

        # 3. Spawn a detached background process to query PyPI when check is due
        if _update_check_is_due():
            # Record check timestamp in main process immediately to prevent concurrent spawns
            _record_update_check()

            # Lazy import popen_resolved_detached to speed up CLI startup time
            from google.agents.cli._runner import popen_resolved_detached
            import sys

            # Non-blocking detached background process using standard urllib
            bg_script = (
                f"import urllib.request, json, pathlib; "
                f"cache = pathlib.Path({repr(str(_LATEST_VERSION_CACHE))}); "
                f"url = 'https://pypi.org/pypi/{PACKAGE_NAME}/json'; "
                f"try: "
                f"  req = urllib.request.Request(url, headers={{'User-Agent': '{PACKAGE_NAME}-bg-check'}}); "
                f"  with urllib.request.urlopen(req, timeout=5) as r: "
                f"    data = json.loads(r.read().decode('utf-8')); "
                f"    ver = data['info']['version']; "
                f"    cache.parent.mkdir(parents=True, exist_ok=True); "
                f"    cache.write_text(ver, encoding='utf-8'); "
                f"except Exception: "
                f"  pass"
            )
            cmd = [sys.executable, "-c", bg_script]
            try:
                popen_resolved_detached(cmd, resolve_executable=False)
            except Exception:
                pass

    except Exception as e:
        # Don't let version checking errors affect the CLI
        logging.debug(f"Error checking for updates: {e}")
