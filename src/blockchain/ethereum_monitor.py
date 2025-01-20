"""
Ethereum blockchain monitoring functionality.
"""

from typing import Dict, Any
from web3 import Web3

from src.utils.time_utils import format_timestamp
import config

class EthereumMonitor:
    def __init__(self, web3: Web3):
        """
        Initialize the Ethereum monitor.
        
        Args:
            web3: Initialized Web3 instance
        """
        self.web3 = web3
        self.known_transactions = set()
        
        # ERC20 creation signatures
        self.erc20_signatures = [
            web3.keccak(text="Transfer(address,address,uint256)").hex(),
            web3.keccak(text="Approval(address,address,uint256)").hex(),
        ]

    def process_transaction(self, tx_hash: str, tx_data: Dict[str, Any]) -> None:
        """
        Process an Ethereum transaction to detect token contract creation.
        
        Analyzes transactions from monitored addresses for contract creation events.
        When a contract is deployed, checks if it matches ERC20 token signatures
        and prints detailed information about the deployment.
        
        Args:
            tx_hash: Transaction hash for blockchain reference
            tx_data: Transaction data including sender, recipient, and other details
        """
        from_address = tx_data.get('from', '').lower()
        
        if from_address not in [addr.lower() for addr in config.ETH_ADDRESSES]:
            return
            
        # Check for contract creation
        if not tx_data.get('to'):
            print(f"\n🔔 [ETHEREUM] POTENTIAL CONTRACT CREATION DETECTED")
            print(f"Time: {format_timestamp(tx_data.get('timestamp'))}")
            print(f"Transaction: {tx_hash}")
            print(f"Creator: {from_address}")
            print(f"Gas Used: {tx_data.get('gasUsed', 'Unknown')}")
            
            # Try to get contract address
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            if receipt and receipt.get('contractAddress'):
                print(f"⭐ NEW CONTRACT ADDRESS: {receipt['contractAddress']}")
                
                # Check if it's an ERC20 token
                contract_code = self.web3.eth.get_code(receipt['contractAddress'])
                for sig in self.erc20_signatures:
                    if sig in str(contract_code):
                        print("✅ Confirmed ERC20 Token Contract")
                        break

    def monitor_addresses(self) -> None:
        """
        Monitor Ethereum addresses for token creation activity.
        
        Continuously checks specified addresses for new transactions in recent blocks
        and analyzes them for token contract creation events. Handles block scanning
        and transaction processing while maintaining a record of known transactions
        to avoid duplicates.
        """
        for address in config.ETH_ADDRESSES:
            try:
                latest_block = self.web3.eth.block_number
                # Look at configured number of blocks
                for block_number in range(latest_block - config.BLOCKS_TO_SCAN, latest_block + 1):
                    block = self.web3.eth.get_block(block_number, full_transactions=True)
                    for tx in block.transactions:
                        tx_hash = tx.get('hash', '').hex()
                        if tx_hash not in self.known_transactions:
                            self.known_transactions.add(tx_hash)
                            self.process_transaction(tx_hash, tx)
            except Exception as e:
                print(f"Error monitoring Ethereum address {address}: {str(e)}")
