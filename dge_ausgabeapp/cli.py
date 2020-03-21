from pathlib import Path

import click
import structlog
from structlog import get_logger

from dge_ausgabeapp import __version__
from dge_ausgabeapp.app import generate_wallet

log = get_logger(__name__)


def configure_logging() -> None:
    structlog.get_config()["processors"].insert(0, structlog.stdlib.add_log_level)


@click.command()
@click.option("-t", "--tax-id", required=True)
@click.option("-a", "--amount", default=1000)
@click.option(
    "-o",
    "--output-dir",
    default=str(Path.cwd().absolute()),
    show_default=True,
    type=click.Path(dir_okay=True, file_okay=False),
)
def main(tax_id: str, amount: int, output_dir: str) -> None:
    configure_logging()
    target_path = Path(output_dir)

    log.info(f"dgE AusgabeApp v{__version__}")

    generate_wallet(tax_id=tax_id, amount_whole_token=amount, target_path=target_path)
    log.info("Done")
