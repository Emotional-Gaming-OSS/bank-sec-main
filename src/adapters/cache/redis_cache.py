"""
Redis Cache Adapter
High-performance caching with Redis
"""

import json
import pickle
from typing import Any, Optional, Union, List
from datetime import timedelta
import redis
from redis.exceptions import RedisError

from src.shared.exceptions import ExternalServiceError
from src.shared.utils.logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Redis cache adapter with connection pooling and error handling"""
    
    def __init__(self, 
                 url: str = "redis://localhost:6379/0",
                 max_connections: int = 50,
                 socket_timeout: int = 5,
                 socket_connect_timeout: int = 5,
                 decode_responses: bool = True):
        """
        Initialize Redis cache
        
        Args:
            url: Redis connection URL
            max_connections: Maximum number of connections in pool
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Connection timeout in seconds
            decode_responses: Whether to decode responses to strings
        """
        self.url = url
        self.max_connections = max_connections
        
        # Connection pool configuration
        connection_pool = redis.ConnectionPool.from_url(
            url=url,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            decode_responses=decode_responses,
            health_check_interval=30
        )
        
        self.redis_client = redis.Redis(connection_pool=connection_pool)
        
        # Test connection
        try:
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {url}")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ExternalServiceError(f"Redis connection failed: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize if it's JSON
            try:
                if isinstance(value, str):
                    return json.loads(value)
                elif isinstance(value, bytes):
                    return pickle.loads(value)
                else:
                    return value
            except (json.JSONDecodeError, pickle.PickleError):
                return value
                
        except RedisError as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    def set(self, 
            key: str, 
            value: Any, 
            ex: Optional[Union[int, timedelta]] = None,
            serialize: str = 'json') -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ex: Expiration time (seconds or timedelta)
            serialize: Serialization method ('json' or 'pickle')
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize value
            if serialize == 'json':
                serialized_value = json.dumps(value, default=str)
            elif serialize == 'pickle':
                serialized_value = pickle.dumps(value)
            else:
                serialized_value = value
            
            return self.redis_client.set(key, serialized_value, ex=ex)
            
        except RedisError as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            return bool(self.redis_client.delete(key))
        except RedisError as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
        
        Returns:
            True if exists, False otherwise
        """
        try:
            return bool(self.redis_client.exists(key))
        except RedisError as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    def expire(self, key: str, time: Union[int, timedelta]) -> bool:
        """
        Set expiration time for existing key
        
        Args:
            key: Cache key
            time: Expiration time
        
        Returns:
            True if successful, False otherwise
        """
        try:
            return bool(self.redis_client.expire(key, time))
        except RedisError as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        Get time to live for key
        
        Args:
            key: Cache key
        
        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        try:
            return self.redis_client.ttl(key)
        except RedisError as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -2
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment numeric value
        
        Args:
            key: Cache key
            amount: Amount to increment by
        
        Returns:
            New value or None if error
        """
        try:
            return self.redis_client.incr(key, amount)
        except RedisError as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return None
    
    def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Decrement numeric value
        
        Args:
            key: Cache key
            amount: Amount to decrement by
        
        Returns:
            New value or None if error
        """
        try:
            return self.redis_client.decr(key, amount)
        except RedisError as e:
            logger.error(f"Redis DECR error for key {key}: {e}")
            return None
    
    def lpush(self, key: str, *values) -> Optional[int]:
        """
        Push values to the left of list
        
        Args:
            key: List key
            *values: Values to push
        
        Returns:
            New list length or None if error
        """
        try:
            return self.redis_client.lpush(key, *values)
        except RedisError as e:
            logger.error(f"Redis LPUSH error for key {key}: {e}")
            return None
    
    def rpop(self, key: str) -> Optional[Any]:
        """
        Pop value from the right of list
        
        Args:
            key: List key
        
        Returns:
            Popped value or None if error
        """
        try:
            return self.redis_client.rpop(key)
        except RedisError as e:
            logger.error(f"Redis RPOP error for key {key}: {e}")
            return None
    
    def sadd(self, key: str, *members) -> Optional[int]:
        """
        Add members to set
        
        Args:
            key: Set key
            *members: Members to add
        
        Returns:
            Number of new members added or None if error
        """
        try:
            return self.redis_client.sadd(key, *members)
        except RedisError as e:
            logger.error(f"Redis SADD error for key {key}: {e}")
            return None
    
    def srem(self, key: str, *members) -> Optional[int]:
        """
        Remove members from set
        
        Args:
            key: Set key
            *members: Members to remove
        
        Returns:
            Number of members removed or None if error
        """
        try:
            return self.redis_client.srem(key, *members)
        except RedisError as e:
            logger.error(f"Redis SREM error for key {key}: {e}")
            return None
    
    def sismember(self, key: str, member) -> Optional[bool]:
        """
        Check if member is in set
        
        Args:
            key: Set key
            member: Member to check
        
        Returns:
            True if member exists, False otherwise, None if error
        """
        try:
            return bool(self.redis_client.sismember(key, member))
        except RedisError as e:
            logger.error(f"Redis SISMEMBER error for key {key}: {e}")
            return None
    
    def hset(self, key: str, field: str, value: Any) -> Optional[int]:
        """
        Set hash field
        
        Args:
            key: Hash key
            field: Field name
            value: Field value
        
        Returns:
            1 if new field, 0 if updated, None if error
        """
        try:
            return self.redis_client.hset(key, field, value)
        except RedisError as e:
            logger.error(f"Redis HSET error for key {key}: {e}")
            return None
    
    def hget(self, key: str, field: str) -> Optional[Any]:
        """
        Get hash field
        
        Args:
            key: Hash key
            field: Field name
        
        Returns:
            Field value or None if not found/error
        """
        try:
            return self.redis_client.hget(key, field)
        except RedisError as e:
            logger.error(f"Redis HGET error for key {key}: {e}")
            return None
    
    def hdel(self, key: str, *fields) -> Optional[int]:
        """
        Delete hash fields
        
        Args:
            key: Hash key
            *fields: Field names to delete
        
        Returns:
            Number of fields deleted or None if error
        """
        try:
            return self.redis_client.hdel(key, *fields)
        except RedisError as e:
            logger.error(f"Redis HDEL error for key {key}: {e}")
            return None
    
    def flushdb(self) -> bool:
        """
        Flush current database (use with caution)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.redis_client.flushdb()
        except RedisError as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False
    
    def info(self) -> Optional[Dict[str, Any]]:
        """
        Get Redis server information
        
        Returns:
            Server info dict or None if error
        """
        try:
            return self.redis_client.info()
        except RedisError as e:
            logger.error(f"Redis INFO error: {e}")
            return None
    
    def ping(self) -> bool:
        """
        Ping Redis server
        
        Returns:
            True if server is responsive, False otherwise
        """
        try:
            return self.redis_client.ping()
        except RedisError:
            return False
    
    def get_connection_pool_info(self) -> Dict[str, Any]:
        """
        Get connection pool information
        
        Returns:
            Connection pool stats
        """
        pool = self.redis_client.connection_pool
        return {
            'max_connections': pool.max_connections,
            'created_connections': pool._created_connections,
            'available_connections': len(pool._available_connections),
            'in_use_connections': len(pool._in_use_connections),
            'url': self.url
        }


class CacheManager:
    """High-level cache manager with automatic serialization and namespacing"""
    
    def __init__(self, redis_cache: RedisCache, namespace: str = "banksec"):
        """
        Initialize cache manager
        
        Args:
            redis_cache: Redis cache instance
            namespace: Key namespace prefix
        """
        self.redis = redis_cache
        self.namespace = namespace
    
    def _namespaced_key(self, key: str) -> str:
        """Add namespace prefix to key"""
        return f"{self.namespace}:{key}"
    
    def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data"""
        return self.redis.get(self._namespaced_key(f"session:{session_id}"))
    
    def set_user_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Set user session data"""
        return self.redis.set(
            self._namespaced_key(f"session:{session_id}"),
            data,
            ex=ttl
        )
    
    def delete_user_session(self, session_id: str) -> bool:
        """Delete user session"""
        return self.redis.delete(self._namespaced_key(f"session:{session_id}"))
    
    def get_scenario_cache(self, scenario_id: int) -> Optional[Dict[str, Any]]:
        """Get scenario from cache"""
        return self.redis.get(self._namespaced_key(f"scenario:{scenario_id}"))
    
    def set_scenario_cache(self, scenario_id: int, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache scenario data"""
        return self.redis.set(
            self._namespaced_key(f"scenario:{scenario_id}"),
            data,
            ex=ttl
        )
    
    def get_user_progress(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user progress from cache"""
        return self.redis.get(self._namespaced_key(f"progress:{user_id}"))
    
    def set_user_progress(self, user_id: int, data: Dict[str, Any], ttl: int = 300) -> bool:
        """Cache user progress"""
        return self.redis.set(
            self._namespaced_key(f"progress:{user_id}"),
            data,
            ex=ttl
        )
    
    def invalidate_user_progress(self, user_id: int) -> bool:
        """Invalidate user progress cache"""
        return self.redis.delete(self._namespaced_key(f"progress:{user_id}"))
    
    def get_rate_limit(self, key: str, window: int = 3600) -> int:
        """Get rate limit counter"""
        count = self.redis.get(self._namespaced_key(f"ratelimit:{key}"))
        return int(count) if count else 0
    
    def increment_rate_limit(self, key: str, window: int = 3600) -> int:
        """Increment rate limit counter"""
        namespaced_key = self._namespaced_key(f"ratelimit:{key}")
        count = self.redis.incr(namespaced_key)
        if count == 1:
            self.redis.expire(namespaced_key, window)
        return count
    
    def clear_namespace(self, pattern: str = "*") -> int:
        """Clear all keys matching pattern in namespace"""
        try:
            cursor = 0
            cleared = 0
            while True:
                cursor, keys = self.redis.redis_client.scan(
                    cursor, 
                    match=self._namespaced_key(pattern),
                    count=100
                )
                if keys:
                    cleared += self.redis.redis_client.delete(*keys)
                if cursor == 0:
                    break
            return cleared
        except RedisError as e:
            logger.error(f"Error clearing namespace {pattern}: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis.info()
            pool_info = self.redis.get_connection_pool_info()
            
            return {
                'redis_version': info.get('redis_version', 'unknown'),
                'used_memory': info.get('used_memory_human', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'cache_hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                ),
                'connection_pool': pool_info
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100


# Global cache instances
def get_cache_manager(url: str = None, namespace: str = "banksec") -> CacheManager:
    """Get configured cache manager"""
    from src.config import get_config
    
    config = get_config()
    redis_url = url or config.REDIS_URL
    
    redis_cache = RedisCache(redis_url)
    return CacheManager(redis_cache, namespace)