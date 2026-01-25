"""
Enhanced API Rotation System for Trading Bot
Complete production-ready system with smart rotation, fault tolerance, proxy support, and stealth capabilities
"""

import asyncio
import aiohttp
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KeyStatus(Enum):
    ACTIVE = "active"
    COOLDOWN = "cooldown"
    FAILED = "failed"

@dataclass
class APIKeyState:
    key: str
    status: KeyStatus = KeyStatus.ACTIVE
    error_count: int = 0
    success_count: int = 0
    consecutive_failures: int = 0
    cooldown_until: Optional[datetime] = None
    last_used: Optional[datetime] = None
    total_requests: int = 0

@dataclass
class ProxyConfig:
    host: str
    port: int
    proxy_type: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: bool = True

class EnhancedAPIRotationSystem:
    """Production-ready API rotation system with all advanced features"""
    
    def __init__(self, api_keys: List[str] = None, proxies: List[Dict] = None):
        # Load keys from api_config.json if not provided
        self.polygon_keys = []
        self.twelve_data_keys = []
        
        if api_keys is None:
            try:
                import json
                with open('api_config.json', 'r') as f:
                    config = json.load(f)
                    self.polygon_keys = config.get('polygon_api_keys', [])
                    self.twelve_data_keys = config.get('twelvedata_api_keys', [])
                    self.primary_provider = config.get('settings', {}).get('primary_provider', 'polygon')
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                # Fallback configuration
                self.polygon_keys = [
                    "M72petEB8NlIu1dT5cROoYBYVGn1U2K_",
                    "EOy9sifOkDRAk7gT2pW4HpVsp6p7I50Q",
                    "yLxw4kPZzDpvmjhNR4ffjBC6rprAVu39"
                ]
                self.twelve_data_keys = [
                    "f5a307fe4b8442f8b9a8795663b75a53",
                    "5d014e9fa4244bb3b3878662bf1df12d"
                ]
                self.primary_provider = 'polygon'
        
        self.api_keys = [APIKeyState(key=key) for key in api_keys]
        self.proxies = []
        self.current_proxy_index = 0
        
        # Initialize proxies if provided
        if proxies:
            for proxy in proxies:
                self.proxies.append(ProxyConfig(**proxy))
        
        self.session = None
        self.base_url = "https://api.twelvedata.com/"
        
        # Performance statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'key_rotations': 0,
            'start_time': datetime.utcnow()
        }
        
        # Request counter for rotation every 2 requests
        self.request_counter = 0
        self.current_key_index = 0
        
        # Enhanced User-Agent strings for stealth
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
        
        logger.info(f"Enhanced API rotation system initialized with {len(self.api_keys)} keys and {len(self.proxies)} proxies")
    
    async def __aenter__(self):
        await self.initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()
    
    async def initialize_session(self):
        """Initialize aiohttp session with Cloudflare bypass capabilities"""
        if not self.session:
            # Enhanced headers to bypass Cloudflare protection
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'Connection': 'keep-alive',
                'DNT': '1'
            }
            
            timeout = aiohttp.ClientTimeout(total=45, connect=15, sock_read=30)
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
                ssl=False  # Disable SSL verification to avoid some blocking
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers
            )
    
    async def close_session(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_random_user_agent(self) -> str:
        """Get random User-Agent for stealth requests"""
        return random.choice(self.user_agents)
    
    def get_next_available_key(self) -> Optional[APIKeyState]:
        """Smart API key selection with round-robin every 2 requests and health checking"""
        now = datetime.utcnow()
        
        # Reset keys from cooldown if time has passed
        for key_state in self.api_keys:
            if key_state.status == KeyStatus.COOLDOWN and key_state.cooldown_until:
                if now > key_state.cooldown_until:
                    key_state.status = KeyStatus.ACTIVE
                    key_state.consecutive_failures = 0
                    key_state.cooldown_until = None
                    logger.info(f"Key ...{key_state.key[-8:]} recovered from cooldown")
        
        # Find available keys
        available_keys = [k for k in self.api_keys if k.status == KeyStatus.ACTIVE]
        
        if not available_keys:
            logger.warning("No available API keys - all may be in cooldown or failed")
            return None
        
        # Increment request counter
        self.request_counter += 1
        
        # Rotate key every 2 requests
        if self.request_counter % 2 == 0:
            self.current_key_index = (self.current_key_index + 1) % len(available_keys)
            self.stats['key_rotations'] += 1
        
        # Get current key, fallback to index 0 if out of bounds
        if self.current_key_index >= len(available_keys):
            self.current_key_index = 0
            
        selected_key = available_keys[self.current_key_index]
        
        logger.debug(f"Selected key ...{selected_key.key[-8:]} (request #{self.request_counter}, rotation every 2)")
        return selected_key
    
    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """Get next proxy using round-robin selection"""
        if not self.proxies:
            return None
        
        active_proxies = [p for p in self.proxies if p.is_active]
        if not active_proxies:
            return None
        
        self.current_proxy_index = (self.current_proxy_index + 1) % len(active_proxies)
        return active_proxies[self.current_proxy_index]
    
    def handle_api_success(self, key_state: APIKeyState):
        """Handle successful API response"""
        key_state.success_count += 1
        key_state.consecutive_failures = 0
        key_state.last_used = datetime.utcnow()
        key_state.total_requests += 1
        
        # Reset status if it was in cooldown
        if key_state.status == KeyStatus.COOLDOWN:
            key_state.status = KeyStatus.ACTIVE
        
        self.stats['successful_requests'] += 1
    
    def handle_api_error(self, key_state: APIKeyState, status_code: int, error_msg: str):
        """Handle API error with intelligent cooldown management"""
        key_state.error_count += 1
        key_state.consecutive_failures += 1
        key_state.last_used = datetime.utcnow()
        key_state.total_requests += 1
        
        self.stats['failed_requests'] += 1
        
        logger.warning(f"API error {status_code} for key ...{key_state.key[-8:]}: {error_msg[:100]}")
        
        # Intelligent cooldown based on error type
        if status_code == 429:  # Rate limit exceeded
            key_state.status = KeyStatus.COOLDOWN
            key_state.cooldown_until = datetime.utcnow() + timedelta(minutes=5)
            logger.info(f"Key rate limited - cooldown for 5 minutes")
            
        elif status_code == 403:  # Forbidden/quota exceeded  
            key_state.status = KeyStatus.COOLDOWN
            key_state.cooldown_until = datetime.utcnow() + timedelta(minutes=10)
            logger.info(f"Key quota exceeded - cooldown for 10 minutes")
            
        elif status_code == 401:  # Unauthorized
            if key_state.consecutive_failures >= 2:
                key_state.status = KeyStatus.FAILED
                logger.error(f"Key appears invalid - marking as failed")
            
        elif status_code >= 500:  # Server errors
            if key_state.consecutive_failures >= 3:
                key_state.status = KeyStatus.COOLDOWN
                key_state.cooldown_until = datetime.utcnow() + timedelta(minutes=2)
                logger.info(f"Server errors - temporary cooldown")
        
        elif key_state.consecutive_failures >= 4:
            # Too many consecutive failures of any type
            key_state.status = KeyStatus.COOLDOWN
            key_state.cooldown_until = datetime.utcnow() + timedelta(minutes=3)
            logger.info(f"Multiple consecutive failures - temporary cooldown")
    
    async def make_request(self, endpoint: str, params: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Enhanced request with smart rotation and fault tolerance"""
        if not self.session:
            await self.initialize_session()
        
        self.stats['total_requests'] += 1
        
        for attempt in range(max_retries):
            # Get next available key
            key_state = self.get_next_available_key()
            if not key_state:
                logger.error("No available API keys")
                await asyncio.sleep(3)
                continue
            
            # Get proxy if available
            proxy = self.get_next_proxy()
            
            # Prepare request
            url = f"{self.base_url}{endpoint}"
            request_params = {**params, 'apikey': key_state.key}
            
            # Enhanced headers for stealth
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            proxy_url = None
            if proxy:
                if proxy.username and proxy.password:
                    proxy_url = f"{proxy.proxy_type}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
                else:
                    proxy_url = f"{proxy.proxy_type}://{proxy.host}:{proxy.port}"
            
            try:
                # Add random delay to avoid Cloudflare rate detection
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
                logger.debug(f"Attempt {attempt + 1}: {endpoint} using key ...{key_state.key[-8:]}")
                
                async with self.session.get(
                    url,
                    params=request_params,
                    headers=headers,
                    proxy=proxy_url,
                    allow_redirects=False  # Don't follow redirects to Cloudflare challenge pages
                ) as response:
                    
                    # Check for Cloudflare challenge page
                    if response.status == 503 or 'cloudflare' in str(response.headers).lower():
                        logger.warning(f"Cloudflare challenge detected, retrying with different approach")
                        await asyncio.sleep(random.uniform(3.0, 6.0))  # Longer delay for Cloudflare
                        continue
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API-level errors in response
                        if isinstance(data, dict) and data.get('status') == 'error':
                            error_msg = data.get('message', 'Unknown API error')
                            self.handle_api_error(key_state, 400, error_msg)
                            continue
                        
                        # Success
                        self.handle_api_success(key_state)
                        logger.debug(f"Successfully fetched {endpoint}")
                        return data
                    
                    else:
                        error_text = await response.text()
                        self.handle_api_error(key_state, response.status, error_text[:200])
                        
                        # Don't retry on certain errors
                        if response.status in [401, 403] and attempt >= 1:
                            break
            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout for {endpoint} with key ...{key_state.key[-8:]}")
                key_state.error_count += 1
                
            except aiohttp.ClientError as e:
                logger.warning(f"Client error for {endpoint}: {e}")
                key_state.error_count += 1
                
            except Exception as e:
                logger.error(f"Unexpected error for {endpoint}: {e}")
                key_state.error_count += 1
            
            # Brief delay between attempts
            if attempt < max_retries - 1:
                await asyncio.sleep(random.uniform(1, 3))
        
        logger.error(f"All {max_retries} attempts failed for {endpoint}")
        return None
    
    async def get_time_series(self, symbol: str, interval: str = '1min', outputsize: int = 100) -> Optional[pd.DataFrame]:
        """Get time series data with enhanced rotation - Direct replacement for existing functions"""
        params = {
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize
        }
        
        data = await self.make_request('time_series', params)
        
        if not data or 'values' not in data:
            logger.warning(f"No data received for {symbol}")
            return None
        
        # Convert to DataFrame format expected by existing bot
        try:
            df_data = []
            for item in data['values']:
                try:
                    df_data.append({
                        'datetime': item.get('datetime'),
                        'open': float(item.get('open', 0)),
                        'high': float(item.get('high', 0)),
                        'low': float(item.get('low', 0)),
                        'close': float(item.get('close', 0)),
                        'volume': float(item.get('volume', 0)) if item.get('volume') else 0
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping invalid data point: {e}")
                    continue
            
            if not df_data:
                return None
            
            df = pd.DataFrame(df_data)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)
            df.sort_index(inplace=True)
            
            logger.debug(f"Successfully converted {len(df)} data points for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error converting data for {symbol}: {e}")
            return None
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price with enhanced rotation"""
        params = {'symbol': symbol}
        
        data = await self.make_request('price', params)
        
        if data and 'price' in data:
            try:
                return float(data['price'])
            except (ValueError, TypeError):
                pass
        
        return None
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote data with enhanced rotation"""
        params = {'symbol': symbol}
        return await self.make_request('quote', params)
    
    async def get_forex_pairs(self) -> Optional[Dict[str, Any]]:
        """Get available forex pairs"""
        return await self.make_request('forex_pairs', {})
    
    async def get_crypto_currencies(self) -> Optional[Dict[str, Any]]:
        """Get available cryptocurrencies"""
        return await self.make_request('cryptocurrencies', {})
    
    async def fetch_data(self, symbol: str, interval: str = '5min', outputsize: int = 100) -> Optional[pd.DataFrame]:
        """Fetch market data - drop-in replacement for existing fetch_data functions"""
        return await self.get_time_series(symbol, interval, outputsize)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        now = datetime.utcnow()
        uptime = (now - self.stats['start_time']).total_seconds()
        
        # Key status summary
        active_keys = sum(1 for k in self.api_keys if k.status == KeyStatus.ACTIVE)
        cooldown_keys = sum(1 for k in self.api_keys if k.status == KeyStatus.COOLDOWN)
        failed_keys = sum(1 for k in self.api_keys if k.status == KeyStatus.FAILED)
        
        # Performance metrics
        total_requests = self.stats['total_requests']
        success_rate = 0
        if total_requests > 0:
            success_rate = (self.stats['successful_requests'] / total_requests) * 100
        
        # Request rate
        requests_per_second = total_requests / uptime if uptime > 0 else 0
        
        return {
            'system_status': {
                'uptime_seconds': round(uptime, 2),
                'status': 'operational' if active_keys > 0 else 'degraded'
            },
            'api_keys': {
                'total': len(self.api_keys),
                'active': active_keys,
                'cooldown': cooldown_keys,
                'failed': failed_keys,
                'utilization': f"{((len(self.api_keys) - active_keys) / len(self.api_keys)) * 100:.1f}%"
            },
            'proxies': {
                'total': len(self.proxies),
                'active': sum(1 for p in self.proxies if p.is_active)
            },
            'performance': {
                'total_requests': total_requests,
                'successful_requests': self.stats['successful_requests'],
                'failed_requests': self.stats['failed_requests'],
                'success_rate': round(success_rate, 2),
                'requests_per_second': round(requests_per_second, 3),
                'key_rotations': self.stats['key_rotations']
            },
            'key_details': [
                {
                    'key_suffix': k.key[-8:],
                    'status': k.status.value,
                    'success_count': k.success_count,
                    'error_count': k.error_count,
                    'success_rate': round((k.success_count / k.total_requests * 100) if k.total_requests > 0 else 0, 1),
                    'cooldown_until': k.cooldown_until.isoformat() if k.cooldown_until else None
                } for k in self.api_keys
            ],
            'timestamp': now.isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        test_result = await self.get_current_price('AAPL')
        
        stats = self.get_system_stats()
        stats['health_check'] = {
            'api_responsive': test_result is not None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return stats

# Global enhanced system instance
_enhanced_system = None

async def get_enhanced_system() -> EnhancedAPIRotationSystem:
    """Get or create the global enhanced system instance"""
    global _enhanced_system
    
    if _enhanced_system is None:
        _enhanced_system = EnhancedAPIRotationSystem()
        await _enhanced_system.__aenter__()
    
    return _enhanced_system

# Drop-in replacement functions for existing bot integration
async def fetch_data(symbol: str, interval: str = '1min', count: int = 100) -> Optional[pd.DataFrame]:
    """
    Enhanced data fetching - Direct replacement for existing fetch_data functions
    Returns DataFrame in the same format as your current implementation
    """
    try:
        system = await get_enhanced_system()
        return await system.get_time_series(symbol, interval, count)
    except Exception as e:
        logger.error(f"Error in fetch_data for {symbol}: {e}")
        return None

async def get_price(symbol: str) -> Optional[float]:
    """Enhanced price fetching - Direct replacement for existing price functions"""
    try:
        system = await get_enhanced_system()
        return await system.get_current_price(symbol)
    except Exception as e:
        logger.error(f"Error in get_price for {symbol}: {e}")
        return None

async def get_quote_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Enhanced quote fetching"""
    try:
        system = await get_enhanced_system()
        return await system.get_quote(symbol)
    except Exception as e:
        logger.error(f"Error in get_quote_data for {symbol}: {e}")
        return None

async def get_system_stats() -> Dict[str, Any]:
    """Get comprehensive system statistics"""
    try:
        system = await get_enhanced_system()
        return system.get_system_stats()
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {'error': str(e)}

async def perform_health_check() -> Dict[str, Any]:
    """Perform system health check"""
    try:
        system = await get_enhanced_system()
        return await system.health_check()
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'error': str(e), 'healthy': False}

async def cleanup():
    """Clean up the enhanced system"""
    global _enhanced_system
    if _enhanced_system:
        await _enhanced_system.__aexit__(None, None, None)
        _enhanced_system = None

# Configuration functions
def configure_proxies(proxies: List[Dict]):
    """Configure proxy settings"""
    global _enhanced_system
    if _enhanced_system:
        _enhanced_system.proxies = [ProxyConfig(**proxy) for proxy in proxies]
        logger.info(f"Configured {len(proxies)} proxies")

def add_api_keys(new_keys: List[str]):
    """Add additional API keys to the rotation"""
    global _enhanced_system
    if _enhanced_system:
        for key in new_keys:
            _enhanced_system.api_keys.append(APIKeyState(key=key))
        logger.info(f"Added {len(new_keys)} new API keys")

# Circuit breaker replacement for existing bot
class EnhancedCircuitBreaker:
    """Enhanced circuit breaker using the smart API rotation system"""
    
    def __init__(self):
        self.state = 'CLOSED'
        self.failure_count = 0
        
    async def call(self, func, *args, **kwargs):
        """Execute function with enhanced error handling"""
        if self.state == 'OPEN':
            # Check system health
            try:
                health = await perform_health_check()
                if health.get('health_check', {}).get('api_responsive', False):
                    self.state = 'CLOSED'
                    self.failure_count = 0
                else:
                    raise Exception("Circuit breaker open - system unhealthy")
            except Exception as e:
                raise Exception(f"Circuit breaker open: {e}")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset failure count
            self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= 3:
                self.state = 'OPEN'
                logger.warning("Enhanced circuit breaker opened due to failures")
            raise e
    
    def reset(self):
        """Reset circuit breaker"""
        self.state = 'CLOSED'
        self.failure_count = 0

# Global circuit breaker instance
enhanced_circuit_breaker = EnhancedCircuitBreaker()