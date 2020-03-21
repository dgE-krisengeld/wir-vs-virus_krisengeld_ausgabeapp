from web3 import Web3, HTTPProvider
#from geth import LiveGethProcess
import json
from web3.middleware import geth_poa_middleware

input_url = "https://"

w3 = Web3(Web3.HTTPProvider(input_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

print(w3.isConnected()) #is everything working correctly
w3.eth.BlockNumer
w3.eth.getBlock('latest')
balance = w3.eth.getBalance("")
print(w3.fromWei(balance, "ether"))

#account creation
#new_account = w3.eth.account.create('New Acc')
#account creation via geth
#geth = LiveGethProcess()
#geth.start()