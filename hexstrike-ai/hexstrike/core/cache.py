"""
HexStrike AI - Caching System
"""
import time
import hashlib
import json
import threading
from collections import OrderedDict
from typing import Any, Dict, Optional

from hexstrike.config import CACHE_SIZE, CACHE_TTL


class HexStrikeCache:
    """LRU Cache dengan TTL untuk command results."""

    def __init__(self, max_size: int = CACHE_SIZE, ttl: int = CACHE_TTL):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}

    def _generate_key(self, command: str, params: Dict[str, Any]) -> str:
        key_data = f"{command}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_expired(self, timestamp: float) -> bool:
        return time.time() - timestamp > self.ttl

    def get(self, command: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        key = self._generate_key(command, params)
        if key in self.cache:
            timestamp, data = self.cache[key]
            if not self._is_expired(timestamp):
                self.cache.move_to_end(key)
                self.stats["hits"] += 1
                return data
            else:
                del self.cache[key]
        self.stats["misses"] += 1
        return None

    def set(self, command: str, params: Dict[str, Any], result: Dict[str, Any]):
        key = self._generate_key(command, params)
        while len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
            self.stats["evictions"] += 1
        self.cache[key] = (time.time(), result)

    def clear(self):
        self.cache.clear()
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}

    def get_stats(self) -> Dict[str, Any]:
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": f"{hit_rate:.1f}%",
            **self.stats,
        }


class AdvancedCache:
    """Thread-safe cache dengan LRU eviction dan TTL."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.ttl_times: Dict[str, float] = {}
        self.cache_lock = threading.RLock()
        self.hit_count = 0
        self.miss_count = 0

        self.cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self.cleanup_thread.start()

    def get(self, key: str) -> Any:
        with self.cache_lock:
            now = time.time()
            if key in self.cache and self.ttl_times.get(key, float('inf')) > now:
                self.access_times[key] = now
                self.hit_count += 1
                return self.cache[key]
            if key in self.cache:
                self._remove_key(key)
            self.miss_count += 1
            return None

    def set(self, key: str, value: Any, ttl: int = None):
        with self.cache_lock:
            now = time.time()
            if ttl is None:
                ttl = self.default_ttl
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            self.cache[key] = value
            self.access_times[key] = now
            self.ttl_times[key] = now + ttl

    def clear(self):
        with self.cache_lock:
            self.cache.clear()
            self.access_times.clear()
            self.ttl_times.clear()

    def _remove_key(self, key: str):
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.ttl_times.pop(key, None)

    def _evict_lru(self):
        if self.access_times:
            lru_key = min(self.access_times, key=self.access_times.get)
            self._remove_key(lru_key)

    def _cleanup_expired(self):
        while True:
            time.sleep(60)
            now = time.time()
            with self.cache_lock:
                expired = [k for k, v in self.ttl_times.items() if v <= now]
                for key in expired:
                    self._remove_key(key)

    def get_stats(self) -> Dict[str, Any]:
        with self.cache_lock:
            total = self.hit_count + self.miss_count
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_count": self.hit_count,
                "miss_count": self.miss_count,
                "hit_rate": (self.hit_count / total * 100) if total > 0 else 0,
            }

# Singleton global (upstream: cache = HexStrikeCache()); dibutuhkan oleh hexstrike/core/__init__.py
cache = HexStrikeCache()
