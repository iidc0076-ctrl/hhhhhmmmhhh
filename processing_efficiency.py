"""
Processing Efficiency Module
Manages system performance, request queuing, and resource optimization
"""

import asyncio
import time
import psutil
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass

class RequestPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class LoadLevel(Enum):
    LIGHT = 1
    MODERATE = 2
    HEAVY = 3
    CRITICAL = 4

class AnalysisMode(Enum):
    FAST = 1
    BALANCED = 2
    COMPREHENSIVE = 3

@dataclass
class SystemPerformance:
    cpu_usage: float
    memory_usage: float
    active_requests: int
    load_level: LoadLevel

class EfficiencyManager:
    def __init__(self):
        self.active_requests = 0
        self.request_queue = asyncio.Queue()
        self.performance_cache = {}
        
    def monitor_performance(self):
        """Monitor system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=None)  # Non-blocking
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > 80 or memory_percent > 80:
            load_level = LoadLevel.CRITICAL
        elif cpu_percent > 60 or memory_percent > 70:
            load_level = LoadLevel.HEAVY
        elif cpu_percent > 40 or memory_percent > 50:
            load_level = LoadLevel.MODERATE
        else:
            load_level = LoadLevel.LIGHT
            
        return SystemPerformance(
            cpu_usage=cpu_percent,
            memory_usage=memory_percent,
            active_requests=self.active_requests,
            load_level=load_level
        )

class DatabaseManager:
    def __init__(self):
        self.cache = {}
        self.last_cleanup = time.time()
        
    async def execute_query(self, query: str, params: tuple = ()):
        """Execute database query with caching"""
        cache_key = f"{query}_{hash(params)}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Simulate query execution
        await asyncio.sleep(0.1)
        result = {"status": "success", "data": []}
        
        self.cache[cache_key] = result
        return result

# Global instances
_efficiency_manager = EfficiencyManager()
_db_manager = DatabaseManager()

def get_efficiency_manager():
    return _efficiency_manager

def get_db_manager():
    return _db_manager

async def queue_analysis_request(request_data: Dict[str, Any], priority: RequestPriority = RequestPriority.NORMAL):
    """Queue analysis request with priority"""
    await _efficiency_manager.request_queue.put((priority.value, time.time(), request_data))
    return True

async def queue_recommendation_request(user_id, function, expiry, mode, num_pairs, user_id_param, recommendation_type, priority: RequestPriority = RequestPriority.NORMAL):
    """Queue recommendation request with priority"""
    request_data = {
        'user_id': user_id,
        'function': function,
        'expiry': expiry,
        'mode': mode,
        'num_pairs': num_pairs,
        'user_id_param': user_id_param,
        'recommendation_type': recommendation_type
    }
    await _efficiency_manager.request_queue.put((priority.value, time.time(), request_data))
    return True

def get_current_analysis_scope():
    """Get current analysis scope based on system load"""
    return AnalysisMode.BALANCED

async def execute_background_task(task_func, *args, **kwargs):
    """Execute background task with resource management"""
    _efficiency_manager.active_requests += 1
    try:
        result = await task_func(*args, **kwargs)
        return result
    finally:
        _efficiency_manager.active_requests -= 1

def get_system_performance():
    """Get current system performance metrics"""
    return _efficiency_manager.monitor_performance()

async def optimized_db_query(query: str, params: tuple = ()):
    """Execute optimized database query"""
    return await _db_manager.execute_query(query, params)