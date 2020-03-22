import json
import os
from pathlib import Path
from typing import Tuple

from eth_keyfile import create_keyfile_json, decode_keyfile_json
from eth_typing import URI, Address
from eth_utils import to_canonical_address
from web3 import HTTPProvider, Web3


def get_web3(rpc_url: str) -> Web3:
    return Web3(HTTPProvider(URI(rpc_url)))


def load_private_key(keystore_path: Path, password: bytes) -> bytes:
    return decode_keyfile_json(json.loads(keystore_path.read_text()), password)


def generate_keystore(password: bytes) -> Tuple[str, Address]:
    privkey = os.urandom(32)
    keyfile_dict = create_keyfile_json(privkey, password=password, iterations=100)
    return json.dumps(keyfile_dict), to_canonical_address(keyfile_dict["address"])


def mint_tokens(
    web3: Web3, local_private_key: bytes, target_address: Address, amount: int
) -> None:
    ...
