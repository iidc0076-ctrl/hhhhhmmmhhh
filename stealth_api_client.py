import asyncio
import aiohttp
import json
import os
import random
import time
from typing import Dict, Optional, Any
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StealthAPIClient:
    """Advanced stealth client for bypassing Cloudflare protection"""
    
    def __init__(self):
        self.session = None
        self.api_key = os.getenv('TWELVEDATA_API_KEY')
        self.base_url = "https://api.twelvedata.com/"
        self.request_count = 0
        self.last_request_time = 0
        
        # Rotating user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'curl/8.5.0',
            'python-requests/2.31.0'
        ]
    
    async def __aenter__(self):
        await self.initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def initialize_session(self):
        """Initialize session with stealth configuration"""
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(
            ssl=False,  # Disable SSL verification for bypass
            limit=5,
            limit_per_host=2
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector
        )
    
    def get_stealth_headers(self) -> Dict[str, str]:
        """Generate stealth headers that mimic real browser requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive'
        }
    
    async def make_stealth_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make request with advanced stealth techniques"""
        if not self.session:
            await self.initialize_session()
        
        # Rate limiting - wait between requests
        current_time = time.time()
        if current_time - self.last_request_time < 3:
            await asyncio.sleep(3 - (current_time - self.last_request_time))
        
        url = f"{self.base_url}{endpoint}"
        request_params = {**params, 'apikey': self.api_key}
        
        headers = self.get_stealth_headers()
        
        try:
            # Random delay before request
            await asyncio.sleep(random.uniform(1, 3))
            
            async with self.session.get(
                url,
                params=request_params,
                headers=headers
            ) as response:
                self.last_request_time = time.time()
                self.request_count += 1
                
                text = await response.text()
                
                # Check for Cloudflare challenge
                if response.status == 403 and 'challenge' in text.lower():
                    logger.warning("Cloudflare challenge detected")
                    return None
                
                if response.status == 200:
                    try:
                        return await response.json()
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON response: {text[:200]}")
                        return None
                else:
                    logger.error(f"Request failed with status {response.status}: {text[:200]}")
                    return None
                    
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    async def get_time_series_data(self, symbol: str, interval: str = '5min', outputsize: int = 100) -> Optional[pd.DataFrame]:
        """Get time series data with stealth techniques"""
        try:
            # First try the time_series endpoint
            data = await self.make_stealth_request('time_series', {
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize,
                'format': 'json'
            })
            
            if data and 'values' in data:
                # Convert to DataFrame
                df = pd.DataFrame(data['values'])
                
                # Handle different response formats
                if len(df.columns) == 6:
                    df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
                elif len(df.columns) == 5:
                    df.columns = ['datetime', 'open', 'high', 'low', 'close']
                    df['volume'] = 0  # Add default volume if missing
                else:
                    logger.error(f"Unexpected number of columns: {len(df.columns)}")
                    return None
                
                # Convert datetime
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)
                
                # Convert to numeric
                numeric_cols = ['open', 'high', 'low', 'close', 'volume']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Sort by datetime
                df = df.sort_index()
                
                logger.info(f"Successfully retrieved {len(df)} data points for {symbol}")
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting time series for {symbol}: {e}")
            return None
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price with stealth request"""
        try:
            data = await self.make_stealth_request('price', {'symbol': symbol})
            
            if data and 'price' in data:
                return float(data['price'])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None

# Global instance
_stealth_client = None

async def get_stealth_client():
    """Get or create stealth client instance"""
    global _stealth_client
    if _stealth_client is None:
        _stealth_client = StealthAPIClient()
    return _stealth_client

async def fetch_market_data_stealth(symbol: str, interval: str = '5min', limit: int = 100) -> Optional[pd.DataFrame]:
    """Fetch market data using stealth client"""
    try:
        async with StealthAPIClient() as client:
            return await client.get_time_series_data(symbol, interval, limit)
    except Exception as e:
        logger.error(f"Stealth fetch error for {symbol}: {e}")
        return None