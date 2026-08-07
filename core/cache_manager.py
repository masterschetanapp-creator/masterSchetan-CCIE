"""
File-based JSON cache system. Each stock gets a folder in cache/ directory.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

try:
    from config import CACHE_DIR, CACHE_TTL
except ImportError:
    CACHE_DIR = "cache"
    CACHE_TTL = {"default": 86400} # 1 day in seconds

def get_stock_cache_dir(symbol: str) -> str:
    """Get the cache directory for a specific symbol."""
    clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
    directory = os.path.join(CACHE_DIR, clean_symbol)
    os.makedirs(directory, exist_ok=True)
    return directory

def get_cache_file_path(symbol: str, module: str) -> str:
    """Get the full path to a cache file."""
    return os.path.join(get_stock_cache_dir(symbol), f"{module}.json")

def is_fresh(symbol: str, module: str) -> bool:
    """Check if cached data is still fresh based on CACHE_TTL from config."""
    file_path = get_cache_file_path(symbol, module)
    if not os.path.exists(file_path):
        return False
        
    ttl = CACHE_TTL.get(module, CACHE_TTL.get('default', 86400))
    mtime = os.path.getmtime(file_path)
    current_time = time.time()
    
    return (current_time - mtime) <= ttl

def get_cached(symbol: str, module: str) -> Optional[Dict[str, Any]]:
    """Get cached data if fresh. Returns None if stale/missing."""
    if not is_fresh(symbol, module):
        return None
        
    file_path = get_cache_file_path(symbol, module)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('data')
    except (json.JSONDecodeError, IOError):
        return None

def set_cached(symbol: str, module: str, data: Dict[str, Any]) -> None:
    """Save data to cache with timestamp."""
    file_path = get_cache_file_path(symbol, module)
    cache_wrapper = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "symbol": symbol,
        "data": data
    }
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cache_wrapper, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Error writing cache for {symbol}/{module}: {e}")

def get_dossier_age(symbol: str) -> str:
    """Returns human-readable age like '2 hours ago' or 'Updated today at 2:30 PM'."""
    file_path = get_cache_file_path(symbol, 'profile') # using profile as base
    if not os.path.exists(file_path):
        return "No data"
        
    mtime = os.path.getmtime(file_path)
    dt = datetime.fromtimestamp(mtime)
    now = datetime.now()
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} minutes ago"
    elif diff < timedelta(hours=24) and dt.date() == now.date():
        return f"Updated today at {dt.strftime('%I:%M %p')}"
    elif diff < timedelta(days=2):
        return f"Updated yesterday at {dt.strftime('%I:%M %p')}"
    else:
        return f"Updated on {dt.strftime('%b %d, %Y')}"
