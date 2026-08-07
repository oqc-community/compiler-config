# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023-2026 Oxford Quantum Circuits Ltd
from dataclasses import fields
from enum import Enum

from compiler_config.config import get_serializable_types as get_base_serializable_types
from compiler_config.serialiser import CustomJSONEncoder


class EradoJSONEncoder(CustomJSONEncoder):
    def default(self, obj):
        from compiler_config.experimental.erado.config import (
            EradoConfig,
            IdlingErrorConfig,
        )

        if isinstance(obj, (EradoConfig, IdlingErrorConfig)):
            return {
                "$type": str(type(obj)),
                "$dataclass": True,
                "$data": {
                    field.name: _serialise_value(getattr(obj, field.name))
                    for field in fields(obj)
                },
            }
        return super().default(obj)


def get_serializable_types():
    from compiler_config.experimental.erado.config import (
        EradoConfig,
        ErasureModel,
        IdleGate,
        IdlingErrorConfig,
    )

    serializable_types = get_base_serializable_types().copy()
    for type_ in (EradoConfig, IdlingErrorConfig, ErasureModel, IdleGate):
        if issubclass(type_, Enum):
            type_name = f"<enum '{type_.__module__}.{type_.__name__}'>"
        else:
            type_name = str(type_)
        serializable_types[type_name] = type_
    return serializable_types


def _serialise_value(value):
    if isinstance(value, Enum):
        return {
            "$type": f"<enum '{value.__module__}.{type(value).__name__}'>",
            "$value": value.value,
        }
    return value
