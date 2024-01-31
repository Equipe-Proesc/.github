from typing import Optional

import typer

from lib.config import app_name, version

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{app_name} v{version}")
        raise typer.Exit()


@app.callback()
def _main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
