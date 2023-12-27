import os
from typing import Optional


def read_env_variable(key: str) -> Optional[str]:
    return os.getenv(key)


def read_env_str(key: str) -> str:
    value_str = read_env_variable(key)
    if value_str is None:
        raise ValueError(f"No environment variable found for {key}")
    return value_str


def read_env_int(key: str) -> int:
    value_str = read_env_variable(key)
    if not value_str:
        raise ValueError(f"Environment variable value for {key} was empty")
    value_int = int(value_str)
    if value_int is None:
        raise ValueError(f"No environment variable found for {key}")
    return value_int


def string_to_bool(string: str) -> bool:
    true_values = ["t", "true", "1"]
    false_values = ["f", "false", "0"]
    if string.lower() in true_values:
        return True
    if string.lower() in false_values:
        return False
    raise ValueError(f"Invalid string that should represent a boolean value: '{string}'")


def read_env_bool(key: str) -> bool:
    value_str = read_env_variable(key)
    if not value_str:
        raise ValueError(f"Environment variable value for {key} was empty")
    value_bool = string_to_bool(value_str)
    if value_bool is None:
        raise ValueError(f"No environment variable found for {key}")
    return value_bool
