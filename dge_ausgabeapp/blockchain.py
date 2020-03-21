import json
import os
from typing import Tuple

from eth_keyfile import create_keyfile_json
from eth_typing import Address
from eth_utils import to_canonical_address
from web3.auto.infura import w3


def generate_keystore(password: bytes) -> Tuple[str, Address]:
    keyfile_dict = create_keyfile_json(os.urandom(32), password=password)
    return json.dumps(keyfile_dict), to_canonical_address(keyfile_dict["address"])


def mint_tokens(address: Address, amount: int) -> None:
    ...

    
def get_account_from_key(w3, key_path, passphrase):
    with open(key_path) as key_file:
        key_json = key_file.read()
    private_key = w3.eth.account.decrypt(key_json, passphrase)
    account = w3.eth.account.privateKeyToAccount(private_key)
    return account

