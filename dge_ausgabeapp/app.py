from datetime import datetime
from pathlib import Path
from typing import Callable

import stdnum.de.idnr
from eth_utils import to_checksum_address
from structlog import get_logger

from dge_ausgabeapp.blockchain import generate_keystore, get_web3, load_private_key, mint_tokens
from dge_ausgabeapp.output import render_paper_wallet

log = get_logger(__name__)


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


def generate_wallet(
    tax_id: str,
    amount_whole_token: int,
    target_path: Path,
    rpc_url: str,
    keystore_path: Path,
    keystore_password: bytes,
) -> None:
    """

    :raises: OSError, stdnum.exceptions.ValidationError
    """

    target_path.mkdir(exist_ok=True)

    generated_password = tax_id_to_password(tax_id=tax_id)
    log.debug("Generating keystore")
    generated_keystore_json, generated_address_bin = generate_keystore(password=generated_password)

    web3 = get_web3(rpc_url=rpc_url)
    local_private_key = load_private_key(keystore_path=keystore_path, password=keystore_password)

    log.info("Minting tokens", amount_whole_token=amount_whole_token)
    mint_tokens(
        web3=web3,
        local_private_key=local_private_key,
        target_address=generated_address_bin,
        amount=amount_whole_token * 10 ** 18,
    )

    target_file_name = Path(tax_id_to_filename_stem(tax_id=tax_id)).with_suffix(".png")
    target_file = target_path.joinpath(target_file_name)

    log.info(
        "Rendering paper wallet",
        address=to_checksum_address(generated_address_bin),
        target_file=str(target_file.relative_to(Path.cwd())),
    )
    print(generated_keystore_json)
    render_paper_wallet(keystore_json=generated_keystore_json, target_file=target_file)
