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

_VERSION = None


def __getattr__(name: str) -> Any:
    """Lazy-load package version to avoid eager importlib.metadata import on startup."""
    global _VERSION
    if name == "__version__":
        if _VERSION is None:
            import importlib.metadata

            try:
                _VERSION = importlib.metadata.version("google-agents-cli")
            except importlib.metadata.PackageNotFoundError:
                _VERSION = "0.0.0-dev"
        return _VERSION
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
