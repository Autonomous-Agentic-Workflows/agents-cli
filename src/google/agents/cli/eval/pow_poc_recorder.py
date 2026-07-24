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

"""Proof of Work (POW) and Proof of Concept (POC) Immutable Recorder Middleware.

Enables legally and technically secure logging of agent executions, establishing
a write-once, cryptographically sealed record of work done and its validated outcome.
"""

from __future__ import annotations

import datetime
import hashlib
import hmac
import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ExecutionStep:
    step_number: int
    action_type: str
    target_uri: str
    dom_snapshot_hash: str
    raw_input_tokens: int
    raw_output_text: str


@dataclass
class CryptographicSeal:
    payload_hash: str
    signature: str


@dataclass
class POWSchema:
    pow_id: str
    timestamp: str
    agent_metadata: dict[str, str]
    execution_steps: list[ExecutionStep] = field(default_factory=list)
    cryptographic_seal: CryptographicSeal | None = None


@dataclass
class TestAssertion:
    assertion: str
    status: str  # PASSED or FAILED
    runtime_ms: int


@dataclass
class POCSchema:
    poc_id: str
    associated_pow_id: str
    ip_asset_id: str
    validation_environment: dict[str, str]
    test_assertions: list[TestAssertion] = field(default_factory=list)
    success_metrics: dict[str, Any] = field(default_factory=dict)


class POWPOCRecorder:
    """Immutable Recorder for capturing and signing agent runs (POW) and validation states (POC)."""

    def __init__(self, agent_id: str, model_version: str, system_prompt: str, ip_asset_id: str):
        self.agent_id = agent_id
        self.model_version = model_version
        self.system_prompt_hash = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()
        self.ip_asset_id = ip_asset_id

        # Generate unique IDs
        timestamp_now = datetime.datetime.utcnow().isoformat() + "Z"
        entropy = f"{agent_id}-{timestamp_now}"
        unique_hash = hashlib.sha256(entropy.encode("utf-8")).hexdigest()[:8]

        self.pow_id = f"pow_{unique_hash}"
        self.poc_id = f"poc_{unique_hash}"

        self.pow = POWSchema(
            pow_id=self.pow_id,
            timestamp=timestamp_now,
            agent_metadata={
                "agent_id": agent_id,
                "model_version": model_version,
                "system_prompt_hash": f"sha256_{self.system_prompt_hash}",
            },
            execution_steps=[],
        )

        self.poc = POCSchema(
            poc_id=self.poc_id,
            associated_pow_id=self.pow_id,
            ip_asset_id=ip_asset_id,
            validation_environment={
                "type": "headless_sandbox_chrome",
                "os": "ubuntu-24.04",
            },
            test_assertions=[],
            success_metrics={
                "compilation_successful": True,
                "rights_conflict_detected": False,
            },
        )

    def record_step(
        self,
        action_type: str,
        target_uri: str,
        page_source: str,
        raw_input_tokens: int,
        raw_output_text: str,
    ) -> ExecutionStep:
        """Capture an execution step and hash the DOM snapshot to prove authenticity."""
        dom_hash = hashlib.sha256(page_source.encode("utf-8")).hexdigest()
        step_number = len(self.pow.execution_steps) + 1

        step = ExecutionStep(
            step_number=step_number,
            action_type=action_type,
            target_uri=target_uri,
            dom_snapshot_hash=f"sha256_{dom_hash}",
            raw_input_tokens=raw_input_tokens,
            raw_output_text=raw_output_text,
        )
        self.pow.execution_steps.append(step)
        return step

    def record_assertion(self, assertion_name: str, passed: bool, runtime_ms: int) -> TestAssertion:
        """Record a test assertion verifying the generated IP plan/rights."""
        status = "PASSED" if passed else "FAILED"
        assertion = TestAssertion(
            assertion=assertion_name,
            status=status,
            runtime_ms=runtime_ms,
        )
        self.poc.test_assertions.append(assertion)

        # If any assertion failed, compilation fails
        if not passed:
            self.poc.success_metrics["compilation_successful"] = False

        return assertion

    def sign_and_commit_bundle(self, signing_key: str) -> dict[str, Any]:
        """Sign the combined POW/POC bundle using HMAC-SHA256 to create a tamper-proof cryptographic seal."""
        pow_data = asdict(self.pow)
        poc_data = asdict(self.poc)

        # Clear any existing seal for hashing
        pow_data["cryptographic_seal"] = None

        payload = {
            "pow": pow_data,
            "poc": poc_data,
        }
        serialized_payload = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(serialized_payload.encode("utf-8")).hexdigest()

        # Generate cryptographic signature
        signature = hmac.new(
            signing_key.encode("utf-8"),
            serialized_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Apply the cryptographic seal
        seal = CryptographicSeal(payload_hash=f"sha256_{payload_hash}", signature=f"0x{signature}")
        self.pow.cryptographic_seal = seal

        # Update final payload with the signature
        payload["pow"]["cryptographic_seal"] = asdict(seal)

        # In production, this dictionary is committed to S3 (WORM mode) or an append-only ledger DB.
        return payload
