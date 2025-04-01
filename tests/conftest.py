from pathlib import Path

SUPPORTED_CONFIG_VERSIONS = ["v02", "v01", "v1"]


class TestType:
    pass


tests_dir = None


def pytest_configure(config):
    global tests_dir
    tests_dir = config.rootpath / "tests"


def _get_json_path(file_name):
    return Path(tests_dir, "serialised_compiler_config_templates", file_name)


def get_contents(file_path):
    """Get Json from a file."""
    with open(_get_json_path(file_path)) as ifile:
        return ifile.read()
