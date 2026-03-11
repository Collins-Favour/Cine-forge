"""
Caching utilities for CineForge AI
Provides Redis-based caching for frequently accessed data
"""
import redis
import json
import pickle
from functools import wraps
from flask import current_app
import os

# Initialize Redis connection
redis_client = None

def get_redis_client():
    """Get or create Redis client"""
    global redis_client
    if redis_client is None:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        try:
            redis_client = redis.from_url(redis_url, decode_responses=False)
            redis_client.ping()  # Test connection
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}. Caching disabled.")
            redis_client = None
    return redis_client


def cache_key(prefix, *args, **kwargs):
    """Generate cache key from prefix and arguments"""
    key_parts = [str(prefix)]
    key_parts.extend([str(arg) for arg in args])
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)


def cache_get(key):
    """Get value from cache"""
    client = get_redis_client()
    if client is None:
        return None
    
    try:
        value = client.get(key)
        if value:
            return pickle.loads(value)
    except Exception as e:
        print(f"Cache get error for {key}: {e}")
    return None


def cache_set(key, value, timeout=300):
    """Set value in cache with timeout (default 5 minutes)"""
    client = get_redis_client()
    if client is None:
        return False
    
    try:
        client.setex(key, timeout, pickle.dumps(value))
        return True
    except Exception as e:
        print(f"Cache set error for {key}: {e}")
        return False


def cache_delete(key):
    """Delete value from cache"""
    client = get_redis_client()
    if client is None:
        return False
    
    try:
        client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error for {key}: {e}")
        return False


def cache_delete_pattern(pattern):
    """Delete all keys matching pattern"""
    client = get_redis_client()
    if client is None:
        return False
    
    try:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
        return True
    except Exception as e:
        print(f"Cache delete pattern error for {pattern}: {e}")
        return False


def cached(timeout=300, key_prefix='view'):
    """
    Decorator to cache function results
    
    Usage:
        @cached(timeout=600, key_prefix='projects')
        def get_user_projects(user_id):
            return Project.query.filter_by(created_by=user_id).all()
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_k = cache_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            result = cache_get(cache_k)
            if result is not None:
                return result
            
            # Call function and cache result
            result = f(*args, **kwargs)
            cache_set(cache_k, result, timeout)
            return result
        return decorated_function
    return decorator


def invalidate_cache(key_prefix, *args, **kwargs):
    """Invalidate specific cache key"""
    cache_k = cache_key(key_prefix, *args, **kwargs)
    cache_delete(cache_k)


def invalidate_project_cache(project_id):
    """Invalidate all cache keys related to a project"""
    patterns = [
        f"*:project:{project_id}:*",
        f"*:projects:*",
        f"*:scenes:project:{project_id}:*",
        f"*:storyboards:project:{project_id}:*",
    ]
    for pattern in patterns:
        cache_delete_pattern(pattern)


def invalidate_user_cache(user_id):
    """Invalidate all cache keys related to a user"""
    patterns = [
        f"*:user:{user_id}:*",
        f"*:projects:user:{user_id}:*",
    ]
    for pattern in patterns:
        cache_delete_pattern(pattern)
