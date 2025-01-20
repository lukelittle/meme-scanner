"""
Blockchain client initialization and connection management.
"""

import os
import sys
from typing import Tuple
from solana.rpc.api import Client as SolanaClient
from web3 import Web3
from web3.exceptions import Web3Exception

import config

def init_blockchain_connections() -> Tuple[SolanaClient, Web3]:
    """
    Initialize and validate connections to Solana and Ethereum networks.
    
    Establishes RPC connections to both blockchains and performs basic
    connectivity tests to ensure the connections are working properly.
    
    Returns:
        Tuple[SolanaClient, Web3]: Initialized Solana and Ethereum clients
        
    Raises:
        SystemExit: If connection fails or required environment variables are missing
    """
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
