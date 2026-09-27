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

"""Tests for skills version check utilities."""

from pathlib import Path
from unittest.mock import patch

from google.agents.cli._skills_check import (
    _find_installed_skills,
    _parse_skill_version,
    check_skills_version,
)


def test_parse_skill_version_unquoted(tmp_path: Path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\nname: test-skill\nmetadata:\n  version: 1.2.3\n---\n# Test",
        encoding="utf-8",
    )
    assert _parse_skill_version(skill_md) == "1.2.3"


def test_parse_skill_version_quoted(tmp_path: Path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        '---\nname: test-skill\nmetadata:\n  version: "2.0.0"\n---\n# Test',
        encoding="utf-8",
    )
    assert _parse_skill_version(skill_md) == "2.0.0"


def test_parse_skill_version_single_quoted(tmp_path: Path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\nname: test-skill\nmetadata:\n  version: '3.1.4'\n---\n# Test",
        encoding="utf-8",
    )
    assert _parse_skill_version(skill_md) == "3.1.4"


def test_parse_skill_version_fallback_complex_yaml(tmp_path: Path):
    # Tests that when regex fast path doesn't match standard version format, PyYAML fallback handles it
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\nname: test-skill\nmetadata:\n  author: Google\n  version: 4.5.6\n---\n# Test",
        encoding="utf-8",
    )
    assert _parse_skill_version(skill_md) == "4.5.6"


def test_parse_skill_version_missing_file(tmp_path: Path):
    skill_md = tmp_path / "nonexistent.md"
    assert _parse_skill_version(skill_md) is None


def test_parse_skill_version_no_frontmatter(tmp_path: Path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("# Just Markdown", encoding="utf-8")
    assert _parse_skill_version(skill_md) is None


def test_parse_skill_version_missing_version(tmp_path: Path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\nname: test-skill\n---\n# Test", encoding="utf-8")
    assert _parse_skill_version(skill_md) is None


def test_find_installed_skills(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skill1 = skills_dir / "google-agents-cli-test1"
    skill1.mkdir(parents=True)
    (skill1 / "SKILL.md").write_text(
        "---\nmetadata:\n  version: 1.0.0\n---\n", encoding="utf-8"
    )

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        skills = _find_installed_skills()
        assert skills == {"google-agents-cli-test1": "1.0.0"}


def test_check_skills_version_mismatch(tmp_path: Path, capsys):
    skills_dir = tmp_path / "skills"
    skill1 = skills_dir / "google-agents-cli-test1"
    skill1.mkdir(parents=True)
    (skill1 / "SKILL.md").write_text(
        "---\nmetadata:\n  version: 0.1.0\n---\n", encoding="utf-8"
    )

    with patch("google.agents.cli._skills_check._is_ci", return_value=False), patch(
        "google.agents.cli._skills_check._skills_check_is_due", return_value=True
    ), patch("pathlib.Path.cwd", return_value=tmp_path), patch(
        "google.agents.cli.__version__", "1.0.0"
    ):
        check_skills_version()
        captured = capsys.readouterr()
        assert "Skills version mismatch" in captured.out
        assert "google-agents-cli-test1 (v0.1.0)" in captured.out
