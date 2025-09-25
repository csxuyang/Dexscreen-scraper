#!/usr/bin/env python3

import asyncio
from curl_cffi.requests import AsyncSession
import urllib.parse
import os
import base64
import json
import re

def generate_sec_websocket_key():
    random_bytes = os.urandom(16)
    key = base64.b64encode(random_bytes).decode('utf-8')
    return key

def is_valid_solana_address_simple(address):
    """Validation đơn giản - chỉ kiểm tra độ dài và ký tự cơ bản"""
    if len(address) != 44:
        return False
    
    # Chỉ kiểm tra ký tự alphanumeric, không quá strict
    if not address.isalnum():
        return False
        
    return True

def extract_pairs_working(data):
    """Parser hoạt động - đơn giản và không quá strict"""

    print(data)
    # Find pairs marker
    pairs_pos = data.find(b'pairs')
    if pairs_pos == -1:
        return []
    
    # Get data after 'pairs'
    pairs_data = data[pairs_pos + 5:]
    
    # Convert to string
    try:
        text_data = pairs_data.decode('utf-8', errors='ignore')
    except:
        return []
    
    pairs = []
    
    # Split theo 'solana'
    sections = text_data.split('solana')[1:]
    
    print(f"🎯 Processing {len(sections)} sections...")
    
    for i, section in enumerate(sections):
        try:
            if len(section) < 20:
                continue
                
            pair = {
                'chain': 'solana', 
                'protocol': 'meteora'
            }
            
            # Tìm label
            if 'DYN2X' in section:
                pair['labels'] = 'DYN2'
                label_pos = section.find('DYN2X')
                after_label = section[label_pos + 5:]
            elif 'DLMMX' in section:
                pair['labels'] = 'DLMM'
                label_pos = section.find('DLMMX')
                after_label = section[label_pos + 5:]
            elif 'DYNX' in section:
                pair['labels'] = 'DYNX'
                label_pos = section.find('DYNX')
                after_label = section[label_pos + 4:]
            else:
                pair['labels'] = 'METEORA'
                after_label = section
            
            # all_addresses = re.findall(r'[A-Za-z0-9]{44}', after_label)
            
            # addresses = []
            # for addr in all_addresses:
            #     if addr not in addresses and len(addr) == 44:
            #         addresses.append(addr)
            
            # # Cần ít nhất 2 addresses
            # if len(addresses) >= 2:
            #     pair['pool'] = addresses[0]
            #     pair['quote'] = addresses[1]
            pair['pool'] = after_label[:44]
            pair['quote'] = after_label[45:89]
                
                # Base token strategy đơn giản:
                # 1. Nếu có SOL address, dùng SOL
                # 2. Nếu có USDC address, dùng USDC  
                # 3. Nếu có address thứ 3, dùng address thứ 3
                
            sol_address = 'So11111111111111111111111111111111111111112'
            usdc_address = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1'
                
            if sol_address in section:
                pair['base'] = sol_address
            elif usdc_address in section:
                pair['base'] = usdc_address
                
            pairs.append(pair)
                
        except Exception as e:
            continue
    
    print(f"✅ Successfully extracted {len(pairs)} pairs")
    return pairs

async def connect_working(rank_by_key: str = "trendingScoreH6", page: int = 1):
    base_uri = f"wss://io.dexscreener.com/dex/screener/v5/pairs/h24/{page}"
    params = {
        "rankBy[key]": rank_by_key,
        "rankBy[order]": "desc",
        "filters[chainIds][0]": "solana"
    }
    uri = f"{base_uri}?{urllib.parse.urlencode(params)}"

    headers = {
        "Host": "io.dexscreener.com",
        "Connection": "Upgrade",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Upgrade": "websocket",
        "Origin": "https://dexscreener.com",
        'Sec-WebSocket-Version': '13',
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Sec-WebSocket-Key": generate_sec_websocket_key()
    }

    print("🚀 WORKING PARSER...")
    
    try:
        session = AsyncSession(headers=headers)
        ws = await session.ws_connect(uri)
        print("✓ Connected!")
        
        message_count = 0
        while message_count < 3:
            try:
                message_tuple = await ws.recv()
                message = message_tuple[0]
                message_count += 1
                
                if message == "ping":
                    await ws.send("pong")
                    continue
                    
                if isinstance(message, bytes):
                    print(f"\n--- Message {message_count} ---")
                    
                    solana_count = message.count(b'solana')
                    print(f"Target: {solana_count} pairs")
                    
                    pairs = extract_pairs_working(message)

                    if len(pairs) > 0:
                        return pairs
                
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        await ws.close()
        return []
        
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    pairs = asyncio.run(connect_working())
    print(pairs)
