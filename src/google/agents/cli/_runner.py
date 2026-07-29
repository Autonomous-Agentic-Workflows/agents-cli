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
    """Check if a key (option name, env var name, etc.) is sensitive."""
    key_lower = key.lower()

    # Ignore non-sensitive terms to prevent false positives
    non_sensitive_terms = ("path", "compat", "pattern", "template", "key_id")
    if any(term in key_lower for term in non_sensitive_terms):
        return False

    # Standardize separator for api-key / api_key and remove leading dashes
    normalized = key_lower.lstrip("-").replace("-", "_")

    # Split key into components by underscores to do precise word matching
    parts = normalized.split("_")

    sensitive_terms = (
        "api_key",
        "token",
        "secret",
        "password",
        "pat",
        "pass",
        "credential",
    )

    for term in sensitive_terms:
        if "_" in term:
            if term in normalized:
                return True
        elif term in ("pat", "pass"):
            if any(part == term for part in parts):
                return True
        elif any(term in part for part in parts):
            return True

    return False


def contains_sensitive_term(s: str) -> bool:
    """Check if a string contains any sensitive term."""
    s_lower = s.lower()

    # Ignore non-sensitive terms to prevent false positives
    non_sensitive_terms = ("path", "compat", "pattern", "template", "key_id")
    if any(term in s_lower for term in non_sensitive_terms):
        return False

    normalized = s_lower.replace("-", "_")
    parts = normalized.split("_")

    sensitive_terms = (
        "api_key",
        "token",
        "secret",
        "password",
        "pat",
        "pass",
        "credential",
    )

    for term in sensitive_terms:
        if "_" in term:
            if term in normalized:
                return True
        elif term in ("pat", "pass"):
            if any(part == term for part in parts):
                return True
        elif any(term in part for part in parts):
            return True

    return False


def redact_value_string(s: str) -> str:
    """Redact sensitive info from a value string which might be a comma-separated list or a single k=v pair."""
    if "," in s:
        parts = s.split(",")
        redacted_parts = []
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                if is_sensitive_key(k):
                    redacted_parts.append(f"{k}=[REDACTED]")
                elif contains_sensitive_term(v):
                    redacted_parts.append("[REDACTED]")
                else:
                    redacted_parts.append(part)
            else:
                if contains_sensitive_term(part):
                    redacted_parts.append("[REDACTED]")
                else:
                    redacted_parts.append(part)
        return ",".join(redacted_parts)
    elif "=" in s:
        k, v = s.split("=", 1)
        if is_sensitive_key(k):
            return f"{k}=[REDACTED]"
        elif contains_sensitive_term(v):
            return "[REDACTED]"
        else:
            return s
    else:
        if contains_sensitive_term(s):
            return "[REDACTED]"
        return s


def redact_cmd(args: list[str]) -> str:
    """Mask sensitive information in command arguments and return joined string.

    Masks arguments like --github-pat, --api-key, --api_key and environment variables containing secrets.
    """
    redacted_cmd_list = list(args)

    for i, raw_arg in enumerate(args):
        arg = str(raw_arg)
        if arg.startswith("-") and "=" not in arg:
            if is_sensitive_key(arg):
                if i + 1 < len(args):
                    redacted_cmd_list[i + 1] = "[REDACTED]"
        elif arg.startswith("-") and "=" in arg:
            opt_name, val = arg.split("=", 1)
            if is_sensitive_key(opt_name):
                redacted_cmd_list[i] = f"{opt_name}=[REDACTED]"
            else:
                redacted_cmd_list[i] = f"{opt_name}={redact_value_string(val)}"
        elif "=" in arg:
            redacted_cmd_list[i] = redact_value_string(arg)
        elif contains_sensitive_term(arg):
            redacted_cmd_list[i] = "[REDACTED]"

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
