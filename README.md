# Multi-Chain Token Creation Monitor

A Python application that monitors token creation events across Solana and Ethereum blockchains.

## Features

- Real-time monitoring of token creation events
- Support for multiple addresses on both chains
- Detection of SPL token and ERC20 token creation
- Detailed transaction information and metadata
- Configurable monitoring parameters

## Prerequisites

- Python 3.8+
- Virtual environment (venv)
- Alchemy API key for Ethereum access

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file and add your Alchemy API key:
- Get an API key from [Alchemy](https://www.alchemy.com/)
- Replace `your-api-key-here` with your actual API key
- Optionally configure custom RPC URLs for Solana and Ethereum

3. Load the environment variables:
```bash
source .env
```

2. Adjust monitoring settings in `config.py`:
- `SOLANA_ADDRESSES`: List of Solana addresses to monitor
- `ETH_ADDRESSES`: List of Ethereum addresses to monitor
- `MONITORING_INTERVAL`: Time between monitoring cycles (seconds)
- `BLOCKS_TO_SCAN`: Number of Ethereum blocks to scan backwards
- `SOLANA_TX_LIMIT`: Number of recent Solana transactions to check

## Usage

Run the monitor:
```bash
python main.py
```

The application will:
1. Validate blockchain connections
2. Display monitoring configuration
3. Start continuous monitoring of specified addresses
4. Print detected token creation events in real-time

## Error Handling

The application includes robust error handling for:
- Missing API keys
- Network connection issues
- Invalid blockchain responses
- Transaction processing errors

## Output Format

### Solana Token Creation
```
🔔 [SOLANA] POTENTIAL NEW TOKEN CREATION DETECTED
Time: YYYY-MM-DD HH:MM:SS PM ET
Transaction: <signature>
Involved Accounts:
Account 0: <address>
⭐ CREATOR ACCOUNT INVOLVED: <address>
```

### Ethereum Token Creation
```
🔔 [ETHEREUM] POTENTIAL CONTRACT CREATION DETECTED
Time: YYYY-MM-DD HH:MM:SS PM ET
Transaction: <hash>
Creator: <address>
Gas Used: <amount>
⭐ NEW CONTRACT ADDRESS: <address>
✅ Confirmed ERC20 Token Contract
