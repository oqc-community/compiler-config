from pathlib import Path

import pytest

SUPPORTED_CONFIG_VERSIONS = ["v02", "v01", "v1"]


class TestType:
    pass


# Derive tests_dir from __file__
tests_dir = Path(__file__).parent
template_dir = tests_dir / "serialised_compiler_config_templates"


def _get_json_path(file_name):
    return template_dir / file_name


def get_contents(file_path):
    """Get Json from a file."""
    with open(_get_json_path(file_path)) as ifile:
        return ifile.read()


# Parameterized fixture for each JSON template file in the templates directory. In other words, any test that
# uses this fixture is tested on all files in the list.
@pytest.fixture(params=template_dir.glob("*.json"))
def json_template_path(request):
    """Yields the name of each JSON template file in the templates directory."""
    return request.param
