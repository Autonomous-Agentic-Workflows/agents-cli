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

# Lazily import importlib.metadata via module __getattr__ to eliminate ~80ms startup
# import overhead when loading CLI subcommands.
_version: str | None = None


def __getattr__(name: str) -> str:
    global _version
    if name == "__version__":
        if _version is None:
            import importlib.metadata

            try:
                _version = importlib.metadata.version("google-agents-cli")
            except importlib.metadata.PackageNotFoundError:
                _version = "0.0.0-dev"
        return _version
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
