import json
import os
from typing import Tuple

from eth_keyfile import create_keyfile_json
from eth_typing import Address
from eth_utils import to_canonical_address


def generate_keystore(password: bytes) -> Tuple[str, Address]:
    keyfile_dict = create_keyfile_json(os.urandom(32), password=password)
    return json.dumps(keyfile_dict), to_canonical_address(keyfile_dict["address"])


def mint_tokens(address: Address, amount: int) -> None:
    ...
