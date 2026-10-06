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

"""Agents CLI — Agent Development Lifecycle toolchain."""

from typing import Any

# Module-level version string cache to prevent repeated imports of importlib.metadata.
_version_cache: str | None = None


def __getattr__(name: str) -> Any:
    """Lazily load __version__ on demand to avoid importing importlib.metadata on module import.

    Deffering importlib.metadata saves ~85-90ms of startup latency when initializing the CLI.
    """
    global _version_cache
    if name == "__version__":
        if _version_cache is None:
            import importlib.metadata

            try:
                _version_cache = importlib.metadata.version("google-agents-cli")
            except importlib.metadata.PackageNotFoundError:
                _version_cache = "0.0.0-dev"
        return _version_cache
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
