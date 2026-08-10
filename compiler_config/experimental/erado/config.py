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


class IdleGate(IntEnum):
    """Gate inserted by Erado when padding idle periods.

    The supported choices are the identity gate and the Pauli X, Y and Z gates.
    """

    IDENTITY = auto()
    PAULI_X = auto()
    PAULI_Y = auto()
    PAULI_Z = auto()


@dataclass
class IdlingErrorConfig:
    """Settings passed to Erado's idle-period padding operation."""

    max_idle_length: int = 14
    idle_gate: IdleGate = IdleGate.IDENTITY
    circuit_gate_time: float = 1.0
    idle_gate_time: float = 0.8
    sequence_min_length_ratio: float = 1.0


@dataclass
class EradoConfig:
    """Configuration for the Erado simulator."""

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

    def from_json(self, json: str):
        vars(self).update(
            vars(json_loads(json, serializable_types=get_serializable_types()))
        )
        return self

    @classmethod
    def create_from_json(cls, json: str):
        return cls().from_json(json)

    def validate(self):
        if not 0 <= self.erasure_rate <= 1:
            raise ValueError("Erasure rate must be between 0 and 1.")
        if self.repeats < 1:
            raise ValueError("Repeats must be positive.")
        if not 0 <= self.false_positive_rate <= 1:
            raise ValueError("False positive rate must be between 0 and 1.")
        if not 0 <= self.false_negative_rate <= 1:
            raise ValueError("False negative rate must be between 0 and 1.")
