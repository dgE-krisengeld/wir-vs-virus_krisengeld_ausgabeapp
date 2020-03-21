import click

from dge_ausgabeapp import __version__


@click.command()
def main() -> None:
    click.secho(f"dgE AusgabeApp v{__version__}", fg="green")
