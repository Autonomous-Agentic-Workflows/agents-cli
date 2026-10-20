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

"""Tests for tombstoned RAG commands and recipe messages."""

import click
import pytest
from click.testing import CliRunner

from google.agents.cli.data._recipe import RAG_RECIPE_MESSAGE
from google.agents.cli.data.cmd_data_ingestion import cmd_data_ingestion
from google.agents.cli.infra.cmd_datastore import cmd_infra_datastore


def test_rag_recipe_message_format():
    """Verify RAG_RECIPE_MESSAGE starts with the visual indicator ✕ and contains helpful context."""
    assert RAG_RECIPE_MESSAGE.startswith("✕ RAG is now a clone-and-study recipe")
    assert "https://github.com/google/adk-samples" in RAG_RECIPE_MESSAGE


def test_cmd_data_ingestion_raises_click_exception():
    """Verify cmd_data_ingestion raises ClickException with RAG_RECIPE_MESSAGE."""
    runner = CliRunner()
    result = runner.invoke(cmd_data_ingestion)
    assert result.exit_code != 0
    assert "✕ RAG is now a clone-and-study recipe" in result.output


def test_cmd_infra_datastore_raises_click_exception():
    """Verify cmd_infra_datastore raises ClickException with RAG_RECIPE_MESSAGE."""
    runner = CliRunner()
    result = runner.invoke(cmd_infra_datastore)
    assert result.exit_code != 0
    assert "✕ RAG is now a clone-and-study recipe" in result.output
