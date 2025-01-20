import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# RPC Endpoints
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
ETH_RPC_URL = os.getenv('ETH_RPC_URL', f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY', '')}")

# Monitored addresses
SOLANA_ADDRESSES: List[str] = [
    "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
    "FUAfBo2jgks6gB4Z4LfZkqSZgzNucisEHqnNebaRxM1P"
]

ETH_ADDRESSES: List[str] = [
    "0x2652067bc90dd89BB67ae6f08A723d58b05E543b"
]

# Monitoring settings
MONITORING_INTERVAL = 15  # seconds
BLOCKS_TO_SCAN = 10  # number of blocks to scan backwards for Ethereum
SOLANA_TX_LIMIT = 5  # number of recent transactions to fetch for each Solana address

# Program IDs
SPL_TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
TOKEN_METADATA_PROGRAM_ID = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
