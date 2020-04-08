import json
import os
from pathlib import Path
from typing import Any, Tuple

from eth_keyfile import create_keyfile_json, decode_keyfile_json
from eth_keys.datatypes import PrivateKey
from eth_typing import URI, Address
from eth_utils import encode_hex, to_canonical_address, to_checksum_address, to_wei
from structlog import get_logger
from web3 import HTTPProvider, Web3
from web3.contract import Contract, ContractFunction
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.types import TxParams, Wei
from yaspin import yaspin
from yaspin.spinners import Spinners

# TODO import this from the contract repo
CONTRACT_PATH = Path(__file__).parent.parent.joinpath("contracts", "dgE.json")


with open(CONTRACT_PATH, "r") as f:
    CONTRACT_ABI = json.load(f)["abi"]

log = get_logger(__name__)


def get_web3(rpc_url: str) -> Web3:
    web3 = Web3(HTTPProvider(URI(rpc_url)))
    web3.eth.setGasPriceStrategy(rpc_gas_price_strategy)  # type: ignore
    return web3


def load_private_key(keystore_path: Path, password: bytes, web3: Web3) -> PrivateKey:
    priv_key = PrivateKey(decode_keyfile_json(json.loads(keystore_path.read_text()), password))
    web3.eth.defaultAccount = priv_key.public_key.to_checksum_address()
    return priv_key


def get_gas_price(web3: Web3) -> Wei:
    gas_price = web3.eth.generateGasPrice()
    assert gas_price is not None, "generateGasPrice returned None!"
    if gas_price == 0:
        gas_price = Wei(to_wei(1, "gwei"))
    return gas_price


def generate_keystore(password: bytes) -> Tuple[str, Address]:
    privkey = os.urandom(32)
    keyfile_dict = create_keyfile_json(privkey, password=password, iterations=100)
    return json.dumps(keyfile_dict), to_canonical_address(keyfile_dict["address"])


def get_token_contract(web3: Web3, token_contract_address: Address) -> Contract:
    log.debug("Contract address", contract_address=to_checksum_address(token_contract_address))
    return web3.eth.contract(address=token_contract_address, abi=CONTRACT_ABI)


def transact_function(web3: Web3, func: "ContractFunction", private_key: bytes) -> None:
    nonce = web3.eth.getTransactionCount(web3.eth.defaultAccount)  # type: ignore
    gas_price = get_gas_price(web3=web3)

    # TODO be better informed about the estimate gas price!
    # estimate_gas = func.estimateGas()  # FIXME this doesn't work

    # Build a transaction that invokes this contract's function, called transfer
    txn = func.buildTransaction(
        TxParams({"gas": Wei(70000), "gasPrice": gas_price, "nonce": nonce})
    )

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)

    send_and_wait_for_transaction(web3=web3, signed_txn=signed_txn)


def send_and_wait_for_transaction(web3: Web3, signed_txn: Any) -> None:
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_hash_hex = encode_hex(tx_hash)
    wait_text = f"Waiting for tx {tx_hash_hex}"
    with yaspin(Spinners.dots2, text=wait_text, color="green", reversal=True):
        receipt = web3.eth.waitForTransactionReceipt(tx_hash, timeout=500)
    assert receipt["blockNumber"] is not None, "TX receipt has empty block number"
    status = receipt.get("status")
    assert status is not None, "TX reciept has no 'status'"
    if status == 0:
        log.error("TX failed", status=status, receipt=receipt)
        raise RuntimeError("Transaction failed")
    log.debug("TX confirmed", tx_hash=tx_hash_hex)


def send_native_coin(
    web3: Web3, local_private_key: PrivateKey, target_address: Address, amount_in_eth: float,
) -> None:
    signed_txn = web3.eth.account.sign_transaction(
        TxParams(
            dict(
                nonce=web3.eth.getTransactionCount(web3.eth.defaultAccount),  # type: ignore
                gasPrice=get_gas_price(web3=web3),
                gas=Wei(21000),
                to=target_address,
                value=Wei(to_wei(amount_in_eth, "ether")),
            )
        ),
        local_private_key,
    )
    log.info(
        "Sending native coin",
        amount_in_whole_units=amount_in_eth,
        target_address=to_checksum_address(target_address),
    )
    send_and_wait_for_transaction(web3=web3, signed_txn=signed_txn)


def mint_tokens(
    web3: Web3,
    local_private_key: PrivateKey,
    token_contract: Contract,
    target_address: Address,
    amount: int,
) -> None:
    log.debug("Minting tokens", amount=amount, target_address=to_checksum_address(target_address))
    mintFor = token_contract.functions.mintFor(target_address, amount)
    transact_function(web3, mintFor, local_private_key)


def whitelist_address(
    web3: Web3, local_private_key: PrivateKey, token_contract: Contract, target_address: Address
) -> None:
    log.info("Whitelisting address", target_address=to_checksum_address(target_address))
    setWhitelistAddress = token_contract.functions.setWhitelistAddress(target_address)
    transact_function(web3, setWhitelistAddress, local_private_key)
    log.info("Successfully whitelisted", target_address=target_address)


def minter_add(
    web3: Web3, local_private_key: PrivateKey, token_contract: Contract, target_address: Address
) -> None:
    log.info("Adding minter", target_address=to_checksum_address(target_address))
    if token_contract.functions.isMinter(target_address).call():
        log.error("Address already is a minter", target_address=target_address)
        return
    transact_function(
        web3=web3,
        func=token_contract.functions.addMinter(target_address),
        private_key=local_private_key,
    )
    log.info("Successfully added minter", target_address=to_checksum_address(target_address))


def minter_remove_self(
    web3: Web3, local_private_key: PrivateKey, token_contract: Contract,
) -> None:
    own_address = local_private_key.public_key.to_checksum_address()
    log.info("Removing self from minters", target_address=own_address)
    if not token_contract.functions.isMinter(own_address).call():
        log.error("Address isn't a minter", target_address=own_address)
        return
    transact_function(
        web3=web3, func=token_contract.functions.renounceMinter(), private_key=local_private_key,
    )
    log.info("Successfully removed self from minters", target_address=own_address)
