#!/usr/bin/env python3

import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
from dex import connect_working
from curl_cffi.requests import AsyncSession
import urllib.parse
import os
import base64

app = FastAPI(title="DexScreener API", description="API for fetching DEX pairs with filters")

def generate_sec_websocket_key():
    random_bytes = os.urandom(16)
    key = base64.b64encode(random_bytes).decode('utf-8')
    return key

async def fetch_pairs_with_filter(rank_by_key: str = "trendingScoreH6", page: int = 1):
    try:
        pairs = await connect_working(rank_by_key, page)
        return pairs
    except Exception as e:
        print(f"Connection error: {e}")
        return []    

@app.get("/")
async def root():
    return {"message": "DexScreener API is running", "endpoints": ["/pairs"]}

@app.get("/pairs")
async def get_pairs(
    rank_by: Optional[str] = Query(
        default="trendingScoreH6", 
        description="Ranking criteria for pairs",
        alias="rankBy[key]"
    ),
    page: Optional[int] = Query(
        default=1,
        description="Page number",
        alias="page"
    )
):
    """
    Fetch DEX pairs with custom ranking filter
    
    Parameters:
    - rank_by: Ranking criteria (default: trendingScoreH6)
    
    Common values:
    - trendingScoreH6: Trending score for 6 hours
    - trendingScoreH1: Trending score for 1 hour  
    - volumeH24: 24-hour volume
    - priceChangeH24: 24-hour price change
    """
    try:
        pairs = await fetch_pairs_with_filter(rank_by, page)
        
        return JSONResponse(content={
            "success": True,
            "filter": {
                "rankBy[key]": rank_by
            },
            "count": len(pairs),
            "data": pairs
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Failed to fetch pairs"
            }
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
