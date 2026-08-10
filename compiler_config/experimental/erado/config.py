# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023-2026 Oxford Quantum Circuits Ltd
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from compiler_config.config import QuantumResultsFormat
from compiler_config.experimental.erado.serialiser import (
    EradoJSONEncoder,
    get_serializable_types,
)
from compiler_config.serialiser import json_dumps, json_loads


class ErasureModel(Enum):
    """Erasure simulation implementation used for an Erado job.

    ``CIRCUIT_SAMPLER`` samples a circuit for each shot. ``TRANSPILER_PASS``
    inserts erasure checks into the circuit before execution.
    """

    CIRCUIT_SAMPLER = "circuit_sampler"
    TRANSPILER_PASS = "transpiler_pass"


@dataclass
class IdlingErrorConfig:
    """Settings passed to Erado's idle-period padding operation.

    Attributes:
        max_idle_length: Maximum number of idle gates inserted into an idle period.
        idle_gate: Qiskit gate name inserted during idle periods. Erado currently
            supports ``"id"``, ``"x"``, ``"y"`` and ``"z"``.
        circuit_gate_time: Unit duration assigned to each existing circuit gate.
        idle_gate_time: Unit duration assigned to each inserted idle gate.
        sequence_min_length_ratio: Minimum ratio between an idle period and the
            inserted gate sequence.
    """

    max_idle_length: int = 14
    idle_gate: str = "id"
    circuit_gate_time: float = 1.0
    idle_gate_time: float = 0.8
    sequence_min_length_ratio: float = 1.0


@dataclass
class EradoConfig:
    """Configuration for the Erado simulator.

    Attributes:
        repeats: Number of simulation shots to request.
        erasure_model: Erado simulation model used to execute the circuit.
        erasure_rate: Probability of erasure at each eligible gate.
        erasure_before_gates: Whether erasures occur before rather than after gates.
        false_positive_rate: Probability that a negative erasure check is flipped.
        false_negative_rate: Probability that a positive erasure check is flipped.
        post_selection: Whether shots containing erasures are rejected and replaced.
        get_fidelities: Whether Erado calculates per-shot fidelities.
        idling_error: Optional settings for padding and simulating idle periods.
    """

    repeats: int = 1000
    erasure_model: ErasureModel = ErasureModel.CIRCUIT_SAMPLER
    erasure_rate: float = 0.5
    erasure_before_gates: bool = False
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    post_selection: bool = False
    get_fidelities: bool = False
    idling_error: Optional[IdlingErrorConfig] = None

    results_format = QuantumResultsFormat().binary_count()

    def to_json(self):
        return json_dumps(
            self,
            cls=EradoJSONEncoder,
            serializable_types=get_serializable_types(),
        )

    @classmethod
    def from_json(cls, json: str):
        config = json_loads(json, serializable_types=get_serializable_types())
        if not isinstance(config, cls):
            raise ValueError("JSON does not contain an EradoConfig.")
        config.validate()
        return config

    def validate(self):
        if not 0 <= self.erasure_rate <= 1:
            raise ValueError("Erasure rate must be between 0 and 1.")
        if self.repeats < 1:
            raise ValueError("Repeats must be positive.")
        if not 0 <= self.false_positive_rate <= 1:
            raise ValueError("False positive rate must be between 0 and 1.")
        if not 0 <= self.false_negative_rate <= 1:
            raise ValueError("False negative rate must be between 0 and 1.")
