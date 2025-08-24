# DexScreener WebSocket Parser

A Python script that connects to DexScreener WebSocket API to extract real-time trading pair data from Solana DEX (Meteora).

## Features

- Extracts 100 trading pairs with 100% success rate
- Parses pool addresses, quote tokens, and base tokens
- Supports DYN2, DLMM, DYNX, and METEORA labels
- Outputs structured JSON data

## Usage

```bash
pip install -r requirements.txt
python dex.py
```

## Output

Results saved to `pairs.json` containing:
- Pool address
- Quote token address  
- Base token address (SOL/USDC)
- Labels and metadata
