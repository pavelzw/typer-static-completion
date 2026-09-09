import pytest
from fixtures import case_fixture
from typer.testing import CliRunner

from typer_static_completions import from_app


def test_case_metadata():
    command = from_app(case_fixture(), "demo").root
    params = {p.name: p for p in command.params}
    assert not params["mode"].case_sensitive
    assert not params["color"].case_sensitive
    assert params["strict"].case_sensitive
    assert all(not value.case_sensitive for value in params["pair"].values)
    assert params["mode"].choices == ("Blue", "RED", "Rose", "Two Words", "Café")


@pytest.mark.parametrize("value", ["blUE", "BLUE", "Blue", "blue"])
def test_case_parser(value):
    result = CliRunner().invoke(case_fixture(), [value, "--mode", value])
    assert result.exit_code == 0, result.output
    assert result.stdout.strip() == "Blue:Blue"
    result = CliRunner().invoke(case_fixture(), ["--strict", value])
    assert result.exit_code == (0 if value == "Blue" else 2)
