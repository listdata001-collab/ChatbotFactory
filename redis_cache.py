"""
Redis caching for knowledge base and frequent queries
Improves performance for high-load scenarios
"""
import os
import json
import redis
import logging
from typing import Optional, Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)

# Redis connection
try:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')  # DB 1 for cache
    redis_client = redis.from_url(redis_url, decode_responses=True)
    # Test connection
    redis_client.ping()
    logger.info("Redis cache connection established")
except Exception as e:
    logger.warning(f"Redis not available, using memory cache: {e}")
    redis_client = None

class MemoryCache:
    """Fallback in-memory cache when Redis unavailable"""
    def __init__(self):
        self._cache = {}
        self._max_size = 1000
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value, ex=None):
        if len(self._cache) >= self._max_size:
            # Remove oldest entries
            keys_to_remove = list(self._cache.keys())[:100]
            for k in keys_to_remove:
                del self._cache[k]
        self._cache[key] = value
    
    def delete(self, key):
        self._cache.pop(key, None)
    
    def exists(self, key):
        return key in self._cache

# Use Redis or fallback to memory cache
cache = redis_client if redis_client else MemoryCache()

def cache_key(prefix: str, *args) -> str:
    """Generate cache key with prefix and arguments"""
    key_parts = [str(arg) for arg in args if arg is not None]
    return f"botfactory:{prefix}:{':'.join(key_parts)}"

def cached_knowledge_base(bot_id: int, ttl: int = 1800) -> Optional[str]:
    """
    Get cached knowledge base for bot (30 min TTL)
    """
    key = cache_key("kb", bot_id)
    try:
        cached_kb = cache.get(key)
        if cached_kb and isinstance(cached_kb, str):
            logger.debug(f"Cache HIT for knowledge base {bot_id}")
            return cached_kb
        logger.debug(f"Cache MISS for knowledge base {bot_id}")
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None

def cache_knowledge_base(bot_id: int, knowledge_base: str, ttl: int = 1800):
    """
    Cache processed knowledge base for bot
    """
    key = cache_key("kb", bot_id)
    try:
        cache.set(key, knowledge_base, ex=ttl)
        logger.debug(f"Cached knowledge base for bot {bot_id}")
    except Exception as e:
        logger.error(f"Cache set error: {e}")

def invalidate_knowledge_base(bot_id: int):
    """
    Invalidate knowledge base cache when updated
    """
    key = cache_key("kb", bot_id)
    try:
        cache.delete(key)
        logger.debug(f"Invalidated knowledge base cache for bot {bot_id}")
    except Exception as e:
        logger.error(f"Cache delete error: {e}")

def cached_user_context(user_id: int, bot_id: int, ttl: int = 300) -> Optional[Dict]:
    """
    Get cached user context (language, subscription, etc.) - 5 min TTL
    """
    key = cache_key("user", user_id, bot_id)
    try:
        cached_data = cache.get(key)
        if cached_data:
            logger.debug(f"Cache HIT for user context {user_id}")
            return json.loads(cached_data)
        return None
    except Exception as e:
        logger.error(f"User context cache error: {e}")
        return None

def cache_user_context(user_id: int, bot_id: int, context: Dict, ttl: int = 300):
    """
    Cache user context data
    """
    key = cache_key("user", user_id, bot_id)
    try:
        cache.set(key, json.dumps(context), ex=ttl)
        logger.debug(f"Cached user context for {user_id}")
    except Exception as e:
        logger.error(f"User context cache set error: {e}")

def rate_limit_check(user_id: int, limit: int = 10, window: int = 60) -> bool:
    """
    Check if user is within rate limits
    Returns True if allowed, False if rate limited
    """
    key = cache_key("rate", user_id)
    try:
        if redis_client:
            current = redis_client.incr(key)
            if isinstance(current, int) and current == 1:
                redis_client.expire(key, window)
            return isinstance(current, int) and current <= limit
        else:
            # Simple rate limiting for memory cache
            return True  # No rate limiting with memory cache
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Allow on error

def cache_ai_response(message_hash: str, response: str, ttl: int = 3600):
    """
    Cache AI responses for identical messages (1 hour TTL)
    """
    key = cache_key("ai_response", message_hash)
    try:
        cache.set(key, response, ex=ttl)
        logger.debug(f"Cached AI response for hash {message_hash[:8]}")
    except Exception as e:
        logger.error(f"AI response cache error: {e}")

def get_cached_ai_response(message_hash: str) -> Optional[str]:
    """
    Get cached AI response for message hash
    """
    key = cache_key("ai_response", message_hash)
    try:
        cached_response = cache.get(key)
        if cached_response:
            logger.debug(f"Cache HIT for AI response {message_hash[:8]}")
            return cached_response
        return None
    except Exception as e:
        logger.error(f"AI response cache get error: {e}")
        return None

def cache_decorator(prefix: str, ttl: int = 300, key_func=None):
    """
    Decorator for caching function results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key_str = key_func(*args, **kwargs)
            else:
                cache_key_str = cache_key(prefix, func.__name__, *args)
            
            # Try to get from cache
            try:
                cached_result = cache.get(cache_key_str)
                if cached_result:
                    logger.debug(f"Cache HIT for {func.__name__}")
                    return json.loads(cached_result)
            except Exception as e:
                logger.error(f"Cache get error in decorator: {e}")
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            try:
                cache.set(cache_key_str, json.dumps(result), ex=ttl)
                logger.debug(f"Cached result for {func.__name__}")
            except Exception as e:
                logger.error(f"Cache set error in decorator: {e}")
            
            return result
        return wrapper
    return decorator

# Health check for cache
def cache_health_check() -> Dict[str, Any]:
    """
    Check cache health and statistics
    """
    try:
        if redis_client:
            info = redis_client.info()
            return {
                'status': 'healthy',
                'type': 'redis',
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        else:
            return {
                'status': 'healthy',
                'type': 'memory',
                'cache_size': len(cache._cache) if hasattr(cache, '_cache') else 0
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }