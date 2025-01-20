"""
Multi-Chain Token Creation Monitor

This script monitors both Solana and Ethereum blockchains for token creation events
from specified wallet addresses. It tracks:
- Solana SPL token creation and metadata updates
- Ethereum ERC20 token contract deployments

The script runs continuously, checking for new transactions at configured intervals
and reporting detailed information about detected token creation events.
"""

from src.monitor import TokenMonitor

def main():
    """Initialize and run the token creation monitor."""
    monitor = TokenMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
