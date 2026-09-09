"""Generate scripts before packaging or installing the example CLI."""

from pathlib import Path

from typer_static_completions import GenerationOptions, write

from .cli import app


def main() -> None:
    outputs = write(
        app,
        "shipyard",
        output_dir=Path("build/completions"),
        options=GenerationOptions(regenerate_command="pixi run example-completions"),
    )
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
