from web3 import Web3, HTTPProvider
from geth import LiveGethProcess
import json

#w3.eth.blockNumber
#w3.eth.getBlock('latest')

w3 = Web3(Web3.HTTPProvider("https://"))
from web3.middleware import geth_poa_middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

w3.isConnected()


#account creation
#new_account = w3.eth.account.create('New Acc')
geth = LiveGethProcess()
geth.start()