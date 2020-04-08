from dataclasses import dataclass
from pathlib import Path

import click
import structlog
from click import Context
from eth_typing import Address
from eth_utils import to_canonical_address
from structlog import get_logger

from dge_ausgabeapp import __version__
from dge_ausgabeapp.app import generate_wallet, minter_add_or_remove, whitelist_acceptance_address

log = get_logger(__name__)


def configure_logging() -> None:
    structlog.get_config()["processors"].insert(0, structlog.stdlib.add_log_level)


@dataclass
class Params:
    keystore_path: Path
    password: bytes
    rpc_url: str
    token_contract_address: Address


@click.group()
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
@click.pass_context
def main(
    ctx: Context, keystore_file: str, password: str, rpc_url: str, contract_address: str,
) -> None:
    configure_logging()
    log.info(f"dgE AusgabeApp v{__version__}")
    token_contract_address = Address(to_canonical_address(contract_address))

    params = Params(
        keystore_path=Path(keystore_file),
        password=password.encode(),
        rpc_url=rpc_url,
        token_contract_address=token_contract_address,
    )
    ctx.obj = params


@main.command()
@click.option("-t", "--tax-id", required=True)
@click.option("-a", "--amount", default=1000)
@click.option(
    "-o",
    "--output-dir",
    default=str(Path.cwd().absolute()),
    show_default=True,
    type=click.Path(dir_okay=True, file_okay=False),
)
@click.pass_obj
def generate(obj: Params, tax_id: str, amount: int, output_dir: str,) -> None:
    target_path = Path(output_dir)
    generate_wallet(
        tax_id=tax_id,
        amount_whole_token=amount,
        target_path=target_path,
        rpc_url=obj.rpc_url,
        keystore_path=obj.keystore_path,
        keystore_password=obj.password,
        token_contract_address=obj.token_contract_address,
    )


@main.command()
@click.option("-a", "--address", required=True)
@click.pass_obj
def whitelist(obj: Params, address: str) -> None:
    whitelist_acceptance_address(
        rpc_url=obj.rpc_url,
        keystore_path=obj.keystore_path,
        keystore_password=obj.password,
        token_contract_address=obj.token_contract_address,
        target_address=to_canonical_address(address),
    )


@main.group(help="Modify the list of minters")
def minter() -> None:
    pass


@minter.command(name="add", help="Add a minter")
@click.option("-a", "--address", required=True)
@click.pass_obj
def cli_minter_add(obj: Params, address: str) -> None:
    minter_add_or_remove(
        rpc_url=obj.rpc_url,
        keystore_path=obj.keystore_path,
        keystore_password=obj.password,
        token_contract_address=obj.token_contract_address,
        target_address=to_canonical_address(address),
        add=True,
    )


@minter.command(name="remove-self", help="Remove oneself from the list of minters")
@click.pass_obj
def cli_minter_remove(obj: Params) -> None:
    minter_add_or_remove(
        rpc_url=obj.rpc_url,
        keystore_path=obj.keystore_path,
        keystore_password=obj.password,
        token_contract_address=obj.token_contract_address,
        target_address=None,
        add=False,
    )
