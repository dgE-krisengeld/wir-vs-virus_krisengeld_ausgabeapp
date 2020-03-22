from pathlib import Path

import click
import structlog
from eth_typing import Address
from eth_utils import to_canonical_address
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
@click.option(
    "-k",
    "--keystore-file",
    type=click.Path(file_okay=True, dir_okay=False, exists=True),
    required=True,
)
@click.password_option("-p", "--password")
@click.option("-r", "--rpc-url", required=True)
@click.option(
    "-c",
    "--contract-address",
    default="0x956604d347412EAD40401af1eba87F0f847A1F01",
    show_default=True,
)
def main(
    tax_id: str,
    amount: int,
    output_dir: str,
    keystore_file: str,
    password: str,
    rpc_url: str,
    contract_address: str,
) -> None:
    configure_logging()
    target_path = Path(output_dir)

    log.info(f"dgE AusgabeApp v{__version__}")

    token_contract_address = Address(to_canonical_address(contract_address))

    generate_wallet(
        tax_id=tax_id,
        amount_whole_token=amount,
        target_path=target_path,
        rpc_url=rpc_url,
        keystore_path=Path(keystore_file),
        keystore_password=password.encode(),
        token_contract_address=token_contract_address,
    )
    log.info("Done")
