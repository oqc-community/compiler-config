# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023-2026 Oxford Quantum Circuits Ltd
import pytest

from compiler_config.experimental.erado.config import (
    EradoConfig,
    ErasureModel,
    IdleGate,
    IdlingErrorConfig,
)


def test_default_config_round_trip():
    config = EradoConfig()

    deserialised_config = EradoConfig.create_from_json(config.to_json())

    assert deserialised_config == config
    assert type(deserialised_config.erasure_model) is ErasureModel
    assert deserialised_config.idling_error is None


def test_full_config_round_trip():
    config = EradoConfig(
        repeats=100,
        erasure_model=ErasureModel.TRANSPILER_PASS,
        erasure_rate=0.25,
        erasure_before_gates=True,
        false_positive_rate=0.1,
        false_negative_rate=0.2,
        post_selection=True,
        get_fidelities=True,
        idling_error=IdlingErrorConfig(
            max_idle_length=8,
            idle_gate=IdleGate.PAULI_Z,
            circuit_gate_time=2.0,
            idle_gate_time=0.5,
            sequence_min_length_ratio=0.75,
        ),
    )

    serialised_config = config.to_json()
    deserialised_config = EradoConfig.create_from_json(serialised_config)

    assert deserialised_config == config
    assert type(deserialised_config.erasure_model) is ErasureModel
    assert type(deserialised_config.idling_error) is IdlingErrorConfig
    assert type(deserialised_config.idling_error.idle_gate) is IdleGate
    assert '"results_format"' not in serialised_config


@pytest.mark.parametrize("value", [1, 1000])
def test_valid_repeats(value):
    EradoConfig(repeats=value).validate()


@pytest.mark.parametrize("value", [0, -1])
def test_invalid_repeats(value):
    with pytest.raises(ValueError, match="Repeats must be positive"):
        EradoConfig(repeats=value).validate()


@pytest.mark.parametrize(
    "field",
    ["erasure_rate", "false_positive_rate", "false_negative_rate"],
)
@pytest.mark.parametrize("value", [0.0, 1.0])
def test_valid_rates(field, value):
    config = EradoConfig()
    setattr(config, field, value)

    config.validate()


@pytest.mark.parametrize(
    "field",
    ["erasure_rate", "false_positive_rate", "false_negative_rate"],
)
@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_rates(field, value):
    config = EradoConfig()
    setattr(config, field, value)

    with pytest.raises(ValueError, match="rate must be between 0 and 1"):
        config.validate()
