from cachetools import TTLCache

# Global cache with default TTL of 5 minutes
_cache = TTLCache(maxsize=1000, ttl=300)

def get(key, default=None):
    """Get value from cache."""
    return _cache.get(key, default)

def set(key, value, ttl=None):
    """Set value in cache (TTL is managed by the cache)."""
    _cache[key] = value

def delete(key):
    """Remove key from cache."""
    if key in _cache:
        del _cache[key]

def clear():
    """Clear all cache."""
    _cache.clear()