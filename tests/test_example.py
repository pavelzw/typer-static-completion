"""Exercise the documented example in the portable CI suite."""

import subprocess
import sys

from typer_static_completions.verify import check_syntax, is_available


def test_example_workflow(tmp_path, monkeypatch):
    from typer.testing import CliRunner

    from examples.cli import app
    from examples.completions import main

    result = CliRunner().invoke(app, ["deploy", "--environment", "staging"])
    assert result.exit_code == 0
    assert "Deploy to staging" in result.stdout
    # Use a subprocess to check the documented module entrypoint too.
    result_cli = subprocess.run(
        [sys.executable, "-m", "examples.cli", "status"],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert result_cli.stdout.strip() == "Ready"
    monkeypatch.chdir(tmp_path)
    main()
    for shell, filename in [
        ("bash", "shipyard"),
        ("fish", "shipyard.fish"),
        ("zsh", "_shipyard"),
    ]:
        script = (tmp_path / "build/completions" / shell / filename).read_text()
        assert "pixi run example-completions" in script
        if is_available(shell):
            check_syntax(script, shell)
