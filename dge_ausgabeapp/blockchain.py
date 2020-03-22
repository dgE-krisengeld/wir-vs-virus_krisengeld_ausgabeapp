import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Tuple

from eth_keyfile import create_keyfile_json, decode_keyfile_json
from eth_typing import URI, Address
from eth_utils import to_bytes, to_canonical_address
from structlog import get_logger
from web3 import HTTPProvider, Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy

if TYPE_CHECKING:
    from web3.contract import ContractFunction

# TODO this is görli for now
CONTRACT_ADDRESS = Address(to_bytes("0x40089B4198f6adCe8F713A501cFb627a38974f79"))
# TODO import this from the contract repo
CONTRACT_PATH = Path(__file__).parent.absolute() / Path("../contracts/dgE.json")


with open(CONTRACT_PATH, "r") as f:
    CONTRACT_ABI = json.load(f)["abi"]

log = get_logger(__name__)


def get_web3(rpc_url: str) -> Web3:
    web3 = Web3(HTTPProvider(URI(rpc_url)))
    web3.eth.setGasPriceStrategy(rpc_gas_price_strategy)  # type: ignore
    return web3


def load_private_key(keystore_path: Path, password: bytes) -> bytes:
    return decode_keyfile_json(json.loads(keystore_path.read_text()), password)


def generate_keystore(password: bytes) -> Tuple[str, Address]:
    privkey = os.urandom(32)
    keyfile_dict = create_keyfile_json(privkey, password=password, iterations=100)
    return json.dumps(keyfile_dict), to_canonical_address(keyfile_dict["address"])


def transact_function(web3: Web3, func: "ContractFunction", private_key: bytes) -> None:
    nonce = web3.eth.getTransactionCount(web3.eth.defaultAccount)  # type: ignore
    gas_price = web3.eth.generateGasPrice()

    # TODO be better informed about the estimate gas price!
    # estimate_gas = func.estimateGas()  # FIXME this doesn't work

    # Build a transaction that invokes this contract's function, called transfer
    txn = func.buildTransaction(
        {"gas": 70000, "gasPrice": gas_price, "nonce": nonce}  # type: ignore
    )

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)

    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    log.debug(f"TXHash received: {web3.toHex(tx_hash)}")
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    log.debug(f"TX receipt received: {tx_receipt}")


def mint_tokens(
    web3: Web3, local_private_key: bytes, target_address: Address, amount: int
) -> None:

    log.debug(f"Contract address: {web3.toHex(CONTRACT_ADDRESS)}")
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    log.info(f"Set address {web3.toChecksumAddress(target_address)} to whitelist.")
    setWhitelistAddress = contract.functions.setWhitelistAddress(target_address)
    transact_function(web3, setWhitelistAddress, local_private_key)

    log.info(f"Mint {amount} dgE for address {web3.toChecksumAddress(target_address)}.")
    mintFor = contract.functions.mintFor(target_address, amount)
    transact_function(web3, mintFor, local_private_key)
