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

"""Subprocess helpers for agents CLI."""

import io
import os
import shlex
import subprocess
import sys
from pathlib import Path

import click

from google.agents.cli import _tools


def is_sensitive_key(key: str) -> bool:
    """Check if a key or flag name contains sensitive credentials."""
    key_lower = key.lower().lstrip("-")
    long_terms = ["api_key", "api-key", "token", "secret", "password", "credential"]
    if any(term in key_lower for term in long_terms):
        return True

    # Check for short terms like 'pat' and 'pass' on snake_case or kebab-case boundaries
    components = [c for c in key_lower.replace("_", "-").split("-") if c]
    if any(c in ("pat", "pass") for c in components):
        return True

    return False


def redact_arg(arg: str) -> str:
    """Redact sensitive components inside a single command argument."""
    # Handle option list arguments that contain commas, e.g. "K1=V1,K2=V2"
    if "," in arg and "=" in arg:
        parts = []
        for p in arg.split(","):
            parts.append(redact_arg(p))
        return ",".join(parts)

    if "=" in arg:
        key, sep, val = arg.partition("=")
        if is_sensitive_key(key):
            return f"{key}=[REDACTED]"

        # If the value contains '=' itself or is a sensitive key-value/credential
        if "=" in val or is_sensitive_key(val):
            if "=" in val:
                redacted_val = redact_arg(val)
                return f"{key}={redacted_val}"
            else:
                return "[REDACTED]"
        return arg

    if is_sensitive_key(arg):
        return "[REDACTED]"

    return arg


def redact_cmd(args: list[str]) -> str:
    """Mask sensitive information in command arguments and return joined string.

    Dynamically and case-insensitively redacts sensitive option flags, KEY=VALUE
    environment variables, and comma-separated option lists.
    """
    redacted_cmd_list = list(args)

    for i, raw_arg in enumerate(args):
        arg = str(raw_arg)
        if (
            arg.startswith("-")
            and "=" not in arg
            and is_sensitive_key(arg)
            and i + 1 < len(args)
        ):
            redacted_cmd_list[i + 1] = "[REDACTED]"
        else:
            # Only update if it hasn't been redacted by a previous flag
            if redacted_cmd_list[i] != "[REDACTED]":
                redacted_cmd_list[i] = redact_arg(arg)

    # Make sure we convert everything to string for shlex.join
    return shlex.join(str(a) for a in redacted_cmd_list)


def run(
    args: list[str],
    *,
    cwd: str | Path | None = None,
    env: dict | None = None,
    capture: bool = False,
    print_cmd: bool = True,
    check: bool = True,
    check_err_msg: str | None = None,
    input_data: bytes | None = None,
    timeout: int | None = None,
    resolve_executable: bool = True,
) -> subprocess.CompletedProcess:
    """Run a subprocess, streaming output by default.

    Args:
        args: Command and arguments.
        cwd: Working directory for the subprocess.
        env: Extra environment variables. Merged with os.environ if provided.
        capture: If True, capture stdout/stderr instead of streaming.
            Defaults to False.
        print_cmd: If True, print the command before executing.
            Defaults to True.
        check: If True, raise ClickException on non-zero exit.
            Defaults to True.
        check_err_msg: Error message prefix for check failures.
        input_data: Bytes to feed to stdin of the subprocess.
        timeout: Timeout in seconds for the subprocess.
        resolve_executable: If True, resolve the executable path using require_tool.
            Defaults to True.

    Returns:
        CompletedProcess instance.
    """
    cmd_str = redact_cmd(args)

    if print_cmd:
        click.secho(f"  ▸ {cmd_str}", fg="cyan", dim=True)

    run_env = None
    if env is not None:
        run_env = {**os.environ, **env}

    # Capture output as UTF-8 text (replacing undecodable bytes) unless we're
    # piping raw bytes to stdin, where child output must stay bytes. Without an
    # explicit encoding, subprocess uses the locale codec + strict errors, which
    # raises UnicodeDecodeError on non-UTF-8 locales (e.g. cp1252 on Windows).
    text_mode = input_data is None
    text_kwargs = {"encoding": "utf-8", "errors": "replace"} if text_mode else {}

    if capture:
        result = run_resolved(
            args,
            resolve_executable=resolve_executable,
            capture_output=True,
            text=text_mode,
            cwd=str(cwd) if cwd else None,
            input=input_data,
            env=run_env,
            timeout=timeout,
            **text_kwargs,
        )
    else:
        # Under click.testing.CliRunner, sys.stdout is a StringIO-like object
        # that doesn't have a fileno(). Subprocess on Windows requires a fileno.
        # We check carefully to avoid issues with mocks or unusual environments.
        use_fallback = True
        if hasattr(sys.stdout, "fileno") and callable(sys.stdout.fileno):
            try:
                sys.stdout.fileno()
                use_fallback = False
            except (io.UnsupportedOperation, AttributeError, OSError):
                pass

        if not use_fallback:
            result = run_resolved(
                args,
                resolve_executable=resolve_executable,
                stdout=sys.stdout,
                stderr=sys.stderr,
                cwd=str(cwd) if cwd else None,
                input=input_data,
                env=run_env,
                timeout=timeout,
            )
        else:
            # Fallback to capture and manual emit for environments without a
            # real stdout fileno (e.g. click.testing.CliRunner).
            result = run_resolved(
                args,
                resolve_executable=resolve_executable,
                capture_output=True,
                text=text_mode,
                cwd=str(cwd) if cwd else None,
                input=input_data,
                env=run_env,
                timeout=timeout,
                **text_kwargs,
            )
            # stdout/stderr are bytes when input_data is set (text=False).
            for stream, content in (
                (sys.stdout, result.stdout),
                (sys.stderr, result.stderr),
            ):
                if not content:
                    continue
                if isinstance(content, bytes):
                    content = content.decode(errors="replace")
                stream.write(content)

    if check and result.returncode != 0:
        error_msg = check_err_msg or f"Command failed: {cmd_str}"
        # When output was captured it never reached the console, so fold it into
        # the error — otherwise the failure reason is lost. Streamed runs already
        # printed it. stdout/stderr are bytes when input_data is set (text=False).
        detail = ""
        if capture:
            captured = "\n".join(
                part.strip()
                for part in (result.stdout, result.stderr)
                if isinstance(part, str) and part.strip()
            )
            if captured:
                detail = f"\n{captured}"
        raise click.ClickException(
            f"{error_msg} (exit code {result.returncode}){detail}"
        )

    return result


def run_resolved(
    args: list[str], *, resolve_executable: bool = True, **kwargs
) -> subprocess.CompletedProcess:
    """Wrapper around subprocess.run with optional executable resolution.

    Args:
        args: Command and arguments as a list of strings.
        resolve_executable: If True, resolve the executable path using require_tool.
            Defaults to True.
        **kwargs: Additional keyword arguments passed to subprocess.run.

    Raises:
        ToolNotFoundError: If resolve_executable is True and the tool cannot be found.

    Returns:
        CompletedProcess instance.
    """
    if isinstance(args, str):
        raise ValueError("args must be a list of strings, not a single string.")

    if resolve_executable and args:
        executable = args[0]
        # Create a shallow copy to avoid modifying the original list passed by reference
        args = args.copy()
        args[0] = _tools.require_tool(executable)

    return subprocess.run(args, **kwargs)


def popen_resolved(
    args: list[str], *, resolve_executable: bool = True, **kwargs
) -> subprocess.Popen:
    """Wrapper around subprocess.Popen with optional executable resolution.

    Args:
        args: Command and arguments as a list of strings.
        resolve_executable: If True, resolve the executable path using require_tool.
            Defaults to True.
        **kwargs: Additional keyword arguments passed to subprocess.Popen.

    Raises:
        ToolNotFoundError: If resolve_executable is True and the tool cannot be found.

    Returns:
        Popen instance.
    """
    if isinstance(args, str):
        raise ValueError("args must be a list of strings, not a single string.")

    if resolve_executable and args:
        executable = args[0]
        # Create a shallow copy to avoid modifying the original list passed by reference
        args = args.copy()
        args[0] = _tools.require_tool(executable)

    return subprocess.Popen(args, **kwargs)


def popen_resolved_detached(
    args: list[str], *, resolve_executable: bool = True, **kwargs
) -> subprocess.Popen:
    """Wrapper around subprocess.Popen for launching detached background processes.

    Handles cross-platform differences for process detaching:
    - On POSIX, sets start_new_session=True.
    - On Windows, sets creationflags to DETACHED_PROCESS and CREATE_NEW_PROCESS_GROUP.
    - Ensures stdin is redirected to subprocess.DEVNULL.

    Args:
        args: Command and arguments as a list of strings.
        resolve_executable: If True, resolve the executable path using require_tool.
            Defaults to True.
        **kwargs: Additional keyword arguments passed to subprocess.Popen.

    Raises:
        ToolNotFoundError: If resolve_executable is True and the tool cannot be found.

    Returns:
        Popen instance.
    """
    stdin = kwargs.get("stdin")
    if stdin is not None and stdin is not subprocess.DEVNULL:
        raise ValueError("popen_resolved_detached only supports stdin=DEVNULL.")
    kwargs["stdin"] = subprocess.DEVNULL

    if os.name == "nt":
        # Windows-specific process creation flags for detaching
        create_new_process_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        create_no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        flags = create_new_process_group | create_no_window
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | flags
    else:
        # POSIX way of detaching
        kwargs["start_new_session"] = True

    return popen_resolved(args, resolve_executable=resolve_executable, **kwargs)
