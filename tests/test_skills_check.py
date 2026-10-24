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

"""Unit tests for _skills_check.py version parsing and drift detection."""

import sys
from pathlib import Path
from google.agents.cli._skills_check import _parse_skill_version


def test_parse_skill_version_unquoted(tmp_path: Path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: test-skill\n"
        "metadata:\n"
        "  author: Google\n"
        "  version: 1.2.3\n"
        "---\n"
        "# Skill Content\n"
    )
    assert _parse_skill_version(skill_md) == "1.2.3"


def test_parse_skill_version_double_quoted(tmp_path: Path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: test-skill\n"
        "metadata:\n"
        '  version: "2.0.0-beta.1"\n'
        "  license: Apache-2.0\n"
        "---\n"
    )
    assert _parse_skill_version(skill_md) == "2.0.0-beta.1"


def test_parse_skill_version_single_quoted(tmp_path: Path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: test-skill\n"
        "metadata:\n"
        "  author: Google\n"
        "  license: Apache-2.0\n"
        "  version: '0.9.1'\n"
        "---\n"
    )
    assert _parse_skill_version(skill_md) == "0.9.1"


def test_parse_skill_version_with_comment(tmp_path: Path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: test-skill\n"
        "metadata:\n"
        "  version: 1.0.0 # initial release\n"
        "---\n"
    )
    assert _parse_skill_version(skill_md) == "1.0.0"


def test_parse_skill_version_fallback(tmp_path: Path):
    # Frontmatter where metadata is defined as flow-style YAML object (regex misses, fallback parses)
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: test-skill\n"
        "metadata: {version: 3.1.4}\n"
        "---\n"
    )
    assert _parse_skill_version(skill_md) == "3.1.4"


def test_parse_skill_version_malformed(tmp_path: Path):
    # Missing frontmatter
    no_fm = tmp_path / "no_fm.md"
    no_fm.write_text("Just markdown without frontmatter")
    assert _parse_skill_version(no_fm) is None

    # Incomplete frontmatter
    inc_fm = tmp_path / "inc_fm.md"
    inc_fm.write_text("---\nname: incomplete\n")
    assert _parse_skill_version(inc_fm) is None

    # Missing metadata version
    no_ver = tmp_path / "no_ver.md"
    no_ver.write_text("---\nname: nover\nmetadata:\n  author: Google\n---\n")
    assert _parse_skill_version(no_ver) is None

    # Non-existent file
    assert _parse_skill_version(tmp_path / "nonexistent.md") is None
