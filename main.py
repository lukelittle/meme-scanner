import os
import sys
import time
from datetime import datetime, timezone
import pytz
from typing import Optional, Dict, List, Any
import json
import base58
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.api import Client as SolanaClient
from web3 import Web3
from web3.exceptions import Web3Exception
import random

import config

def format_timestamp(unix_timestamp: Optional[int]) -> str:
    if not unix_timestamp:
        return "N/A"
    utc_time = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    eastern = pytz.timezone('America/New_York')
    eastern_time = utc_time.astimezone(eastern)
    return eastern_time.strftime("%Y-%m-%d %I:%M:%S %p ET")

def get_current_time() -> str:
    eastern = pytz.timezone('America/New_York')
    return datetime.now(eastern).strftime("%Y-%m-%d %I:%M:%S %p ET")

print("\n===== MULTI-CHAIN TOKEN CREATION MONITOR =====")
print(f"Start Time: {get_current_time()}\n")

def init_blockchain_connections():
    """Initialize and validate blockchain connections"""
    try:
        solana_client = SolanaClient(config.SOLANA_RPC_URL)
        # Test Solana connection
        solana_client.is_connected()
    except Exception as e:
        print(f"Error connecting to Solana network: {str(e)}")
        sys.exit(1)

    if not os.getenv('ALCHEMY_API_KEY'):
        print("Error: ALCHEMY_API_KEY environment variable is required")
        sys.exit(1)

    try:
        eth_w3 = Web3(Web3.HTTPProvider(config.ETH_RPC_URL))
        if not eth_w3.is_connected():
            raise Web3Exception("Failed to connect to Ethereum network")
    except Exception as e:
        print(f"Error connecting to Ethereum network: {str(e)}")
        sys.exit(1)

    return solana_client, eth_w3

# Initialize blockchain connections
solana_client, eth_w3 = init_blockchain_connections()

# Critical program IDs
SPL_TOKEN_PROGRAM_ID = Pubkey.from_string(config.SPL_TOKEN_PROGRAM_ID)
TOKEN_METADATA_PROGRAM_ID = Pubkey.from_string(config.TOKEN_METADATA_PROGRAM_ID)

# ERC20 creation signatures
ERC20_CREATION_SIGNATURES = [
    eth_w3.keccak(text="Transfer(address,address,uint256)").hex(),
    eth_w3.keccak(text="Approval(address,address,uint256)").hex(),
]

print("Monitoring Configuration:")
print("\nSolana Addresses:")
for addr in config.SOLANA_ADDRESSES:
    print(f"- {addr}")
print("\nEthereum Addresses:")
for addr in config.ETH_ADDRESSES:
    print(f"- {addr}")

known_transactions = {
    'solana': set(),
    'ethereum': set()
}
new_tokens = {
    'solana': set(),
    'ethereum': set()
}

def process_solana_instruction(instruction: Dict, accounts: List[str], tx_signature: str, timestamp: int) -> None:
    """Process Solana instruction for token creation"""
    if not isinstance(instruction, dict):
        return

    program_id = instruction.get("programId")
    if not program_id:
        return
    
    monitored_involved = any(addr in accounts for addr in config.SOLANA_ADDRESSES)
    
    if not monitored_involved:
        return
        
    if program_id == str(SPL_TOKEN_PROGRAM_ID):
        print(f"\n🔔 [SOLANA] POTENTIAL NEW TOKEN CREATION DETECTED")
        print(f"Time: {format_timestamp(timestamp)}")
        print(f"Transaction: {tx_signature}")
        print("\nInvolved Accounts:")
        for idx, account in enumerate(accounts):
            print(f"Account {idx}: {account}")
            if account in config.SOLANA_ADDRESSES:
                print(f"⭐ CREATOR ACCOUNT INVOLVED: {account}")
    
    elif program_id == str(TOKEN_METADATA_PROGRAM_ID):
        print(f"\n📝 [SOLANA] TOKEN METADATA CREATION DETECTED")
        print(f"Time: {format_timestamp(timestamp)}")
        print(f"Transaction: {tx_signature}")
        print("\nInvolved Accounts:")
        for idx, account in enumerate(accounts):
            print(f"Account {idx}: {account}")

def process_eth_transaction(tx_hash: str, tx_data: Dict) -> None:
    """Process Ethereum transaction for token creation"""
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
        receipt = eth_w3.eth.get_transaction_receipt(tx_hash)
        if receipt and receipt.get('contractAddress'):
            print(f"⭐ NEW CONTRACT ADDRESS: {receipt['contractAddress']}")
            
            # Check if it's an ERC20 token
            contract_code = eth_w3.eth.get_code(receipt['contractAddress'])
            for sig in ERC20_CREATION_SIGNATURES:
                if sig in str(contract_code):
                    print("✅ Confirmed ERC20 Token Contract")
                    break

def monitor_all_chains():
    print("\nStarting multi-chain token creation monitoring...")
    interval = config.MONITORING_INTERVAL
    loop_count = 0

    while True:
        try:
            loop_count += 1
            print(f"\n===== MONITORING ITERATION {loop_count} | {get_current_time()} =====")
            
            # Monitor Solana addresses
            for pubkey in [Pubkey.from_string(addr) for addr in config.SOLANA_ADDRESSES]:
                try:
                    response = solana_client.get_signatures_for_address(pubkey, limit=config.SOLANA_TX_LIMIT)
                    if hasattr(response, 'value') and response.value:
                        for sig in response.value:
                            signature = str(sig.signature)
                            if signature not in known_transactions['solana']:
                                known_transactions['solana'].add(signature)
                                
                                try:
                                    print(f"Fetching transaction {signature}...")
                                    tx_response = solana_client._provider.make_request(
                                        "getTransaction",
                                        [
                                            signature,
                                            {
                                                "encoding": "jsonParsed",
                                                "maxSupportedTransactionVersion": 0
                                            }
                                        ]
                                    )
                                    
                                    if not tx_response or "result" not in tx_response:
                                        print(f"Invalid response format for transaction {signature}")
                                        continue

                                    tx_data = tx_response["result"]
                                    if not tx_data:
                                        continue

                                    # Extract transaction details from the JSON response
                                    transaction = tx_data.get("transaction", {})
                                    message = transaction.get("message", {})
                                    
                                    # Get account keys and instructions
                                    account_keys = [acc.get("pubkey") for acc in message.get("accountKeys", [])]
                                    instructions = message.get("instructions", [])
                                    
                                    # Process each instruction
                                    for instruction in instructions:
                                        process_solana_instruction(
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
            
            # Monitor Ethereum addresses
            for address in config.ETH_ADDRESSES:
                try:
                    latest_block = eth_w3.eth.block_number
                    # Look at configured number of blocks
                    for block_number in range(latest_block - config.BLOCKS_TO_SCAN, latest_block + 1):
                        block = eth_w3.eth.get_block(block_number, full_transactions=True)
                        for tx in block.transactions:
                            tx_hash = tx.get('hash', '').hex()
                            if tx_hash not in known_transactions['ethereum']:
                                known_transactions['ethereum'].add(tx_hash)
                                process_eth_transaction(tx_hash, tx)
                except Exception as e:
                    print(f"Error monitoring Ethereum address {address}: {str(e)}")
            
            time.sleep(interval)
            
        except Exception as e:
            print(f"Monitor error: {str(e)}")
            time.sleep(interval)

if __name__ == "__main__":
    monitor_all_chains()
