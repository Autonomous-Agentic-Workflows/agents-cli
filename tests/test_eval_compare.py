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

import json
from click.testing import CliRunner

from google.agents.cli.eval.cmd_compare import cmd_compare


def test_eval_compare_table_default():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("baseline.json", "w", encoding="utf-8") as f:
            json.dump({"accuracy": 0.85, "latency": 1.2, "status": "ok"}, f)
        with open("candidate.json", "w", encoding="utf-8") as f:
            json.dump({"accuracy": 0.92, "latency": 1.0, "status": "ok"}, f)

        result = runner.invoke(cmd_compare, ["baseline.json", "candidate.json"])
        assert result.exit_code == 0
        assert "Evaluation Comparison" in result.output
        assert "baseline.json" in result.output
        assert "candidate.json" in result.output
        assert "accuracy" in result.output
        assert "0.8500" in result.output
        assert "0.9200" in result.output
        assert "+0.0700" in result.output


def test_eval_compare_json_format():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("baseline.json", "w", encoding="utf-8") as f:
            json.dump({"accuracy": 0.85}, f)
        with open("candidate.json", "w", encoding="utf-8") as f:
            json.dump({"accuracy": 0.92}, f)

        result = runner.invoke(
            cmd_compare, ["baseline.json", "candidate.json", "--format", "json"]
        )
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert "differences" in parsed
        assert "accuracy" in parsed["differences"]
        assert parsed["differences"]["accuracy"]["baseline"] == 0.85
        assert parsed["differences"]["accuracy"]["candidate"] == 0.92


def test_eval_compare_no_differences():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("baseline.json", "w", encoding="utf-8") as f:
            json.dump({"accuracy": 0.85}, f)
        with open("candidate.json", "w", encoding="utf-8") as f:
            json.dump({"accuracy": 0.85}, f)

        result = runner.invoke(cmd_compare, ["baseline.json", "candidate.json"])
        assert result.exit_code == 0
        assert "No differences found between baseline and candidate." in result.output
