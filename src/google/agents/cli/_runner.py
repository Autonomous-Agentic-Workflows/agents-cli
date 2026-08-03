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
    """Check if a key (case-insensitive, hyphen-agnostic) is sensitive."""
    key_lower = key.lower().lstrip("-").replace("_", "-")
    for term in ("api-key", "api_key", "token", "secret", "password", "credential"):
        normalized_term = term.replace("_", "-")
        if normalized_term in key_lower:
            return True

    # Short terms boundary check (exact snake_case or kebab-case components)
    components = [c for c in key_lower.split("-") if c]
    for term in ("pat", "pass"):
        if term in components:
            return True

    return False


def contains_sensitive(s: str) -> bool:
    """Check if string s (case-insensitive) contains any sensitive term."""
    s_lower = s.lower().replace("_", "-")
    for term in ("api-key", "api_key", "token", "secret", "password", "credential"):
        normalized_term = term.replace("_", "-")
        if normalized_term in s_lower:
            return True

    cleaned = "".join(c if c.isalnum() else "-" for c in s_lower)
    components = [comp for comp in cleaned.split("-") if comp]
    for term in ("pat", "pass"):
        if term in components:
            return True

    return False


def redact_cmd(args: list[str]) -> str:
    """Mask sensitive information in command arguments and return joined string.

    Masks arguments like --github-pat, --api-key, --api_key and environment variables containing secrets.
    """
    redacted_cmd_list = list(args)
    redact_next = False

    for i, raw_arg in enumerate(args):
        arg = str(raw_arg)

        # 1. If we are told to redact the next argument
        if redact_next:
            redacted_cmd_list[i] = "[REDACTED]"
            redact_next = False
            continue

        # 2. Check if the argument is a sensitive option flag itself (e.g. --api-key, --github-pat)
        # It must start with "-" and NOT contain "="
        if arg.startswith("-") and "=" not in arg:
            # Strip leading hyphens to get flag name
            flag_name = arg.lstrip("-")
            if is_sensitive_key(flag_name):
                # The next argument should be redacted
                redact_next = True
                continue

        # 3. Handle cases where the argument contains "="
        # (e.g. KEY=VALUE, --api-key=VALUE, or key1=val1,key2=val2)
        if "=" in arg:
            # We can have a comma-separated list of options
            parts = arg.split(",")
            new_parts = []
            any_redacted = False
            for part in parts:
                if "=" in part:
                    k, sep, v = part.partition("=")
                    # Strip leading hyphens from key for sensitive check
                    clean_k = k.lstrip("-")
                    if is_sensitive_key(clean_k):
                        new_parts.append(f"{k}=[REDACTED]")
                        any_redacted = True
                    elif contains_sensitive(part):
                        # Even if the key is not sensitive, if the whole part contains sensitive info,
                        # redact the whole part
                        new_parts.append("[REDACTED]")
                        any_redacted = True
                    else:
                        new_parts.append(part)
                else:
                    # No '=' in this part, check if it contains sensitive info
                    if contains_sensitive(part):
                        new_parts.append("[REDACTED]")
                        any_redacted = True
                    else:
                        new_parts.append(part)

            if any_redacted:
                redacted_cmd_list[i] = ",".join(new_parts)
                continue

        # 4. If argument has no "=" but contains sensitive info
        if contains_sensitive(arg):
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
