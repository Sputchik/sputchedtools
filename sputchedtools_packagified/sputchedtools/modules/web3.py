from web3 import Web3
from typing import Union
from time import sleep

__all__ = ['Web3Misc']

class Web3Misc:

	"""
	Methods:
		- gas_monitor()
		- gas_price_monitor()
		- nonce_monitor()
		- get_nonce()

	Attributes:
		- web3: web3.Web3 instance

	"""

	def __init__(self, web3: Web3):

		self.web3 = web3
		self.gas = None
		self.gas_price = None
		self.nonce = None

	def gas_monitor(
		self,
		token_contract,
		sender: str,
		period: Union[float, int] = 10,
		multiply_by: float = 1.0
	):
		dead = '0x000000000000000000000000000000000000dEaD'

		while True:
			self.gas = round(token_contract.functions.transfer(dead, 0).estimate_gas({'from': sender}) * multiply_by)
			sleep(period)

	def gas_price_monitor(
		self,
		period: Union[float, int] = 10,
		multiply_by: float = 1.0
	):

		while True:
			self.gas_price = round(self.web3.eth.gas_price * multiply_by)
			sleep(period)

	def nonce_monitor(
		self,
		address: str,
		period: Union[float, int] = 10
	):

		while True:
			self.nonce = self.web3.eth.get_transaction_count(address)
			sleep(period)

	def get_nonce(self, address: str) -> int:
		return self.web3.eth.get_transaction_count(address)