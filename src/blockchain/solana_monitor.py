"""
Solana blockchain monitoring functionality.
"""

from typing import Dict, List, Any
import base58
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.api import Client as SolanaClient

from src.utils.time_utils import format_timestamp
import config

class SolanaMonitor:
    def __init__(self, client: SolanaClient):
        """
        Initialize the Solana monitor.
        
        Args:
            client: Initialized Solana RPC client
        """
        self.client = client
        self.known_transactions = set()
        
        # Critical program IDs
        self.spl_token_program_id = str(Pubkey.from_string(config.SPL_TOKEN_PROGRAM_ID))
        self.token_metadata_program_id = str(Pubkey.from_string(config.TOKEN_METADATA_PROGRAM_ID))

    def process_instruction(self, instruction: Dict[str, Any], accounts: List[str], tx_signature: str, timestamp: int) -> None:
        """
        Process a Solana transaction instruction to detect token creation events.
        
        Analyzes transaction instructions for SPL token program and metadata program
        interactions that indicate token creation or metadata updates. Prints detailed
        information when token-related activities are detected from monitored addresses.
        
        Args:
            instruction: Dictionary containing instruction data including program ID
            accounts: List of account public keys involved in the transaction
            tx_signature: Transaction signature for blockchain reference
            timestamp: Unix timestamp of the transaction
        """
        program_id = str(instruction.program_id)
        
        monitored_involved = any(addr in accounts for addr in config.SOLANA_ADDRESSES)
        
        if not monitored_involved:
            return
            
        if program_id == self.spl_token_program_id:
            print(f"\n🔔 [SOLANA] POTENTIAL NEW TOKEN CREATION DETECTED")
            print(f"Time: {format_timestamp(timestamp)}")
            print(f"Transaction: {tx_signature}")
            print("\nInvolved Accounts:")
            for idx, account in enumerate(accounts):
                print(f"Account {idx}: {account}")
                if account in config.SOLANA_ADDRESSES:
                    print(f"⭐ CREATOR ACCOUNT INVOLVED: {account}")
        
        elif program_id == self.token_metadata_program_id:
            print(f"\n📝 [SOLANA] TOKEN METADATA CREATION DETECTED")
            print(f"Time: {format_timestamp(timestamp)}")
            print(f"Transaction: {tx_signature}")
            print("\nInvolved Accounts:")
            for idx, account in enumerate(accounts):
                print(f"Account {idx}: {account}")

    def monitor_addresses(self) -> None:
        """
        Monitor Solana addresses for token creation activity.
        
        Continuously checks specified addresses for new transactions and analyzes them
        for token creation events. Handles transaction fetching and processing while
        maintaining a record of known transactions to avoid duplicates.
        """
        for pubkey in [Pubkey.from_string(addr) for addr in config.SOLANA_ADDRESSES]:
            try:
                response = self.client.get_signatures_for_address(pubkey, limit=config.SOLANA_TX_LIMIT)
                if hasattr(response, 'value') and response.value:
                    for sig in response.value:
                        signature = str(sig.signature)
                        if signature not in self.known_transactions:
                            self.known_transactions.add(signature)
                            
                            try:
                                print(f"Fetching transaction {signature}...")
                                # Convert string signature to Signature object
                                sig_obj = Signature.from_string(signature)
                                
                                # Get transaction using Signature object
                                tx_response = self.client.get_transaction(
                                    sig_obj,
                                    max_supported_transaction_version=0
                                )
                                
                                if not tx_response or not tx_response.value:
                                    print(f"No data found for transaction {signature}")
                                    continue

                                tx_data = tx_response.value
                                
                                # Debug print to understand structure
                                print(f"Transaction data structure: {tx_data}")
                                print(f"Transaction object structure: {tx_data.transaction}")
                                
                                # Extract transaction details from parsed data
                                message = tx_data.transaction.message
                                
                                # Get account keys and instructions
                                account_keys = [str(key) for key in message.account_keys]
                                instructions = message.instructions
                                
                                # Process each instruction
                                for instruction in instructions:
                                    self.process_instruction(
                                        instruction,
                                        account_keys,
                                        signature,
                                        sig.block_time
                                    )
                            except Exception as e:
                                print(f"Error getting transaction {signature}: {str(e)}")
                                continue
            except Exception as e:
                print(f"Error monitoring Solana address {str(pubkey)}: {str(e)}")
