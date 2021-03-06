import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import quote

import stdnum.de.idnr
from eth_typing import Address
from eth_utils import to_checksum_address
from structlog import get_logger

from dge_ausgabeapp.blockchain import (
    generate_keystore,
    get_token_contract,
    get_web3,
    load_private_key,
    mint_tokens,
    minter_add,
    minter_remove_self,
    send_native_coin,
    whitelist_address,
)
from dge_ausgabeapp.output import render_paper_wallet

log = get_logger(__name__)

TARGET_URL_BASE = "https://bundesburner.web.app/open/"


def tax_id_to_password(tax_id: str) -> bytes:
    """
    Validates a German Tax ID and returnes a compact represenation (only numbers, no spaces).

    :raises: stdnum.exceptions.ValidationError
    """
    stdnum.de.idnr.validate(tax_id)
    log.debug("Tax ID valid", tax_id=tax_id)
    return stdnum.de.idnr.compact(tax_id).encode()


def tax_id_to_filename_stem(
    tax_id: str, now_callable: Callable[[], datetime] = datetime.now
) -> str:
    tax_id_formatted = stdnum.de.idnr.format(tax_id).replace(" ", "-")
    return f"wallet_{tax_id_formatted}_{now_callable():%Y-%m-%dT%H-%M-%S}"


def make_url_from_keystore_json(
    keystore_json: str, _target_url_base: str = TARGET_URL_BASE
) -> str:
    return f"{_target_url_base}{quote(keystore_json)}"


def generate_wallet(
    tax_id: str,
    amount_whole_token: int,
    target_path: Path,
    rpc_url: str,
    keystore_path: Path,
    keystore_password: bytes,
    token_contract_address: Address,
) -> None:
    """

    :raises: OSError, stdnum.exceptions.ValidationError
    """

    target_path.mkdir(exist_ok=True)

    generated_password = tax_id_to_password(tax_id=tax_id)
    generated_keystore_json, generated_address_bin = generate_keystore(password=generated_password)
    log.debug("Generated keystore", address=to_checksum_address(generated_address_bin))

    web3 = get_web3(rpc_url=rpc_url)
    local_private_key = load_private_key(
        keystore_path=keystore_path, password=keystore_password, web3=web3
    )

    log.info("Minting dgE tokens", amount_whole_token=amount_whole_token)
    token_contract = get_token_contract(web3, token_contract_address=token_contract_address)
    mint_tokens(
        web3=web3,
        local_private_key=local_private_key,
        token_contract=token_contract,
        target_address=generated_address_bin,
        amount=amount_whole_token * 10 ** 18,
    )

    send_native_coin(
        web3=web3,
        local_private_key=local_private_key,
        target_address=generated_address_bin,
        amount_in_eth=0.001,
    )

    target_file_name = Path(tax_id_to_filename_stem(tax_id=tax_id)).with_suffix(".pdf")
    target_file_path = target_path.joinpath(target_file_name)

    generated_keystore_urlified = make_url_from_keystore_json(
        keystore_json=generated_keystore_json
    )

    log.info(
        "Rendering paper wallet", target_file=str(target_file_path.relative_to(Path.cwd())),
    )
    render_paper_wallet(qr_data=generated_keystore_urlified, target_file_path=target_file_path)
    webbrowser.open(f"file://{target_file_path.absolute()}")
    log.info("Done")


def whitelist_acceptance_address(
    rpc_url: str,
    keystore_path: Path,
    keystore_password: bytes,
    token_contract_address: Address,
    target_address: Address,
) -> None:
    web3 = get_web3(rpc_url=rpc_url)
    local_private_key = load_private_key(
        keystore_path=keystore_path, password=keystore_password, web3=web3
    )
    token_contract = get_token_contract(web3, token_contract_address=token_contract_address)

    whitelist_address(
        web3=web3,
        local_private_key=local_private_key,
        token_contract=token_contract,
        target_address=target_address,
    )
    log.info("Done")


def minter_add_or_remove(
    rpc_url: str,
    keystore_path: Path,
    keystore_password: bytes,
    token_contract_address: Address,
    target_address: Optional[Address],
    add: bool,
) -> None:
    web3 = get_web3(rpc_url=rpc_url)
    local_private_key = load_private_key(
        keystore_path=keystore_path, password=keystore_password, web3=web3
    )
    token_contract = get_token_contract(web3, token_contract_address=token_contract_address)

    if add:
        assert target_address is not None, "Adding a minter requires an address"
        minter_add(
            web3=web3,
            local_private_key=local_private_key,
            token_contract=token_contract,
            target_address=target_address,
        )
    else:
        minter_remove_self(
            web3=web3, local_private_key=local_private_key, token_contract=token_contract,
        )
    log.info("Done")
