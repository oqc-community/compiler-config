# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Oxford Quantum Circuits Ltd

from sys import __loader__

import pytest
from conftest import SUPPORTED_CONFIG_VERSIONS, TestType, get_contents

from compiler_config.config import (
    CompilerConfig,
    InlineResultsProcessing,
    MetricsType,
    OptimizationConfig,
    Qasm2Optimizations,
    QiskitOptimizations,
    QuantumResultsFormat,
    ResultsFormatting,
    Tket,
    TketOptimizations,
)


def test_config_opt_contains():
    opt = Qasm2Optimizations()
    assert TketOptimizations.DefaultMappingPass in opt
    assert QiskitOptimizations.Empty in opt


def test_default_config():
    first_conf = CompilerConfig()
    serialized_data = first_conf.to_json()
    second_conf = CompilerConfig.create_from_json(serialized_data)

    assert first_conf.results_format.format == second_conf.results_format.format
    assert first_conf.results_format.transforms == second_conf.results_format.transforms

    conf1_dict = dict(vars(first_conf))
    del conf1_dict["results_format"]
    conf2_dict = dict(vars(second_conf))
    del conf2_dict["results_format"]

    assert conf1_dict == conf2_dict


def test_specific_config_optimizations():
    first_conf = CompilerConfig()
    first_conf.optimizations = Qasm2Optimizations()
    serialized_data = first_conf.to_json()
    second_conf = CompilerConfig.create_from_json(serialized_data)
    assert (
        first_conf.optimizations.tket_optimizations
        == second_conf.optimizations.tket_optimizations
    )
    assert (
        first_conf.optimizations.qiskit_optimizations
        == second_conf.optimizations.qiskit_optimizations
    )


@pytest.mark.parametrize(
    "pre_select, post_select", [(True, True), (True, False), (False, True), (False, False)]
)
def test_pre_post_selection_serialisation(pre_select, post_select):
    """
    Test that the pre_selection and post_selection fields are correctly serialised and deserialised
    in the CompilerConfig object. Ensures that both True and False values for these fields are
    preserved through the serialisation-deserialisation process.
    """
    local_config = CompilerConfig(pre_selection=pre_select, post_selection=post_select)
    serialized_data = local_config.to_json()
    assert '"pre_selection":' in serialized_data
    assert '"post_selection":' in serialized_data

    decode_config = CompilerConfig.create_from_json(serialized_data)
    assert decode_config.pre_selection == pre_select
    assert decode_config.post_selection == post_select


def test_pre_post_selection_backwards_compatibility(json_template):
    config = CompilerConfig.create_from_json(get_contents(json_template))
    assert config.pre_selection is False
    assert config.post_selection is False


def test_all_config_optimizations():
    def get_subclasses(object):
        subclasses = []

        def find_subclasses(obj):
            for subclass in obj.__subclasses__():
                subclasses.append(subclass)
                find_subclasses(subclass)

        find_subclasses(object)

        return subclasses

    optimizations = get_subclasses(OptimizationConfig)

    first_conf = CompilerConfig()

    for optimization in optimizations:
        first_conf.optimizations = optimization()
        serialized_data = first_conf.to_json()
        second_conf = CompilerConfig.create_from_json(serialized_data)

        assert vars(first_conf.optimizations) == vars(second_conf.optimizations)


def test_config_repeats():
    first_conf = CompilerConfig()
    first_conf.repeats = 1000
    first_conf.repetition_period = 10
    serialized_data = first_conf.to_json()
    second_conf = CompilerConfig.create_from_json(serialized_data)

    assert first_conf.repeats == second_conf.repeats
    assert first_conf.repetition_period == second_conf.repetition_period


def test_config_metrics():
    first_conf = CompilerConfig()

    for value in MetricsType:
        first_conf.metrics = value
        serialized_data = first_conf.to_json()
        second_conf = CompilerConfig.create_from_json(serialized_data)

        assert first_conf.metrics == second_conf.metrics


def test_config_quantum_results_format():
    first_conf = CompilerConfig()

    for format in InlineResultsProcessing:
        for transform in ResultsFormatting:
            first_conf.results_format = QuantumResultsFormat()
            first_conf.results_format.format = format
            first_conf.results_format.transforms = transform
            serialized_data = first_conf.to_json()
            second_conf = CompilerConfig.create_from_json(serialized_data)

            assert first_conf.results_format == second_conf.results_format


def test_config_serialisation_raises_error():
    class A:
        pass

    first_conf = CompilerConfig()
    first_conf.optimizations = A()  # A is not an allowed type

    with pytest.raises(ValueError):
        first_conf.to_json()

    first_conf.optimizations = TestType  # Not an allowed custom type in project

    with pytest.raises(ValueError):
        first_conf.to_json()

    first_conf.optimizations = __loader__  # Not an allowed type from system module

    with pytest.raises(ValueError):
        first_conf.to_json()


def test_config_deserialization_raises_error():
    serialized_data = str(
        {
            "$type": "<class 'scc.compiler.config.FakeClass'>",
            "$data": {"repeats": 1000, "repetition_period": 1000},
        }
    )
    with pytest.raises(ValueError):
        CompilerConfig.create_from_json(serialized_data)


@pytest.mark.parametrize("version", SUPPORTED_CONFIG_VERSIONS)
def test_json_version_compatibility_default(version):
    serialised_data = get_contents(f"serialised_default_compiler_config_{version}.json")
    deserialised_conf = CompilerConfig.create_from_json(serialised_data)
    assert deserialised_conf.metrics == MetricsType.Default
    assert deserialised_conf.results_format == QuantumResultsFormat()


@pytest.mark.parametrize("version", SUPPORTED_CONFIG_VERSIONS)
def test_json_version_compatibility_full(version):
    serialised_data = get_contents(f"serialised_full_compiler_config_{version}.json")
    deserialised_conf = CompilerConfig.create_from_json(serialised_data)
    assert deserialised_conf.repeats == 1000
    assert deserialised_conf.repetition_period == 10
    assert deserialised_conf.metrics == MetricsType.OptimizedInstructionCount
    assert deserialised_conf.results_format.format == InlineResultsProcessing.Binary
    assert (
        deserialised_conf.results_format.transforms
        == ResultsFormatting.DynamicStructureReturn
    )
    assert deserialised_conf.optimizations.qiskit_optimizations == QiskitOptimizations.Empty
    assert deserialised_conf.optimizations.tket_optimizations == TketOptimizations.One


@pytest.mark.parametrize("flag", [to for to in TketOptimizations])
def test_tket_flags(flag):
    tket = None
    if flag == TketOptimizations.GlobalisePhasedX:
        with pytest.warns(DeprecationWarning):
            tket = Tket(tket_optimization=flag)
    else:
        tket = Tket(tket_optimization=flag)
    assert flag in tket
