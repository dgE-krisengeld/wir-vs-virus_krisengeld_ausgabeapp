import json
import os
from typing import Tuple

from eth_keyfile import create_keyfile_json
from eth_typing import URI, Address
from eth_utils import to_canonical_address
from web3 import HTTPProvider, Web3
from web3.middleware import geth_poa_middleware


def print_balance(address: Address, web3: Web3) -> None:
    balance = web3.eth.getBalance(address)
    print(web3.fromWei(balance, "ether"))  # prints etherium balance


def print_connection_status(web3: Web3) -> None:
    print(web3.isConnected())  # is everything working correctly


def generate_keystore(password: bytes) -> Tuple[str, Address]:
    keyfile_dict = create_keyfile_json(os.urandom(32), password=password)
    return json.dumps(keyfile_dict), to_canonical_address(keyfile_dict["address"])


def mint_tokens(address: Address, amount: int) -> None:
    input_url = "https://"
    w3 = Web3(HTTPProvider(URI(input_url)))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.eth.getBlock("latest")
