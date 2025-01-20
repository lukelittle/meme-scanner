"""
Main token creation monitoring orchestrator.
"""

import time
from typing import Dict, Set

from src.blockchain.clients import init_blockchain_connections
from src.blockchain.solana_monitor import SolanaMonitor
from src.blockchain.ethereum_monitor import EthereumMonitor
from src.utils.time_utils import get_current_time
import config

class TokenMonitor:
    """
    Main token creation monitoring orchestrator.
    
    Coordinates monitoring of both Solana and Ethereum blockchains for token
    creation events, managing the individual blockchain monitors and providing
    a unified interface for the monitoring process.
    """
    
    def __init__(self):
        """Initialize the token monitor and its blockchain-specific components."""
        # Initialize blockchain connections
        self.solana_client, self.eth_w3 = init_blockchain_connections()
        
        # Initialize blockchain-specific monitors
        self.solana_monitor = SolanaMonitor(self.solana_client)
        self.ethereum_monitor = EthereumMonitor(self.eth_w3)
        
        # Print initial configuration
        self._print_config()

    def _print_config(self) -> None:
        """Print the current monitoring configuration."""
        print("\n===== MULTI-CHAIN TOKEN CREATION MONITOR =====")
        print(f"Start Time: {get_current_time()}\n")
        
        print("Monitoring Configuration:")
        print("\nSolana Addresses:")
        for addr in config.SOLANA_ADDRESSES:
            print(f"- {addr}")
        print("\nEthereum Addresses:")
        for addr in config.ETH_ADDRESSES:
            print(f"- {addr}")

    def run(self) -> None:
        """
        Start the monitoring process.
        
        Continuously monitors both blockchains for token creation events,
        coordinating between the Solana and Ethereum monitors while handling
        any errors that occur during the process.
        """
        print("\nStarting multi-chain token creation monitoring...")
        interval = config.MONITORING_INTERVAL
        loop_count = 0

        while True:
            try:
                loop_count += 1
                print(f"\n===== MONITORING ITERATION {loop_count} | {get_current_time()} =====")
                
                # Monitor Solana
                self.solana_monitor.monitor_addresses()
                
                # Monitor Ethereum
                self.ethereum_monitor.monitor_addresses()
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Monitor error: {str(e)}")
                time.sleep(interval)
