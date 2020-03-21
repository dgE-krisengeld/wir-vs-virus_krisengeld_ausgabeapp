import json
import os

from eth_keyfile import create_keyfile_json
from eth_typing import Address
from web3.auto.infura import w3


def generate_keystore(password: str) -> str:
    return json.dumps(create_keyfile_json(os.urandom(32), password=password))


def mint_tokens(address: Address, amount: int) -> None:
    w3.eth.blockNumber
    w3.eth.getBlock("latest")
