from web3 import Web3
from threading import Thread

w3 = Web3(Web3.HTTPProvider('https://arbitrum.meowrpc.com'))

from sputchedtools import Web3Misc

misc = Web3Misc(w3)

Thread(target = misc.gas_price_monitor).start()
import time
while True:
	print(misc.gas)
	time.sleep(1)