import json
import os

from eth_keyfile import create_keyfile_json
from eth_typing import Address
from web3.auto.infura import w3
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware


input_url = "https://"
w3 = Web3(Web3.HTTPProvider(input_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.BlockNumer
w3.eth.getBlock('latest')
    
    
def print_balance() -> None:
    balance = w3.eth.getBalance("")
    print(w3.fromWei(balance, "ether")) #prints etherium balance

def print_connection_status() -> None:
    print(w3.isConnected()) #is everything working correctly


def generate_keystore(password: str) -> str:
    return json.dumps(create_keyfile_json(os.urandom(32), password=password))


def mint_tokens(address: Address, amount: int) -> None:
    w3.eth.blockNumber
    w3.eth.getBlock("latest")
