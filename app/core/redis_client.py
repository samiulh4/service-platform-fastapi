from typing import Optional, Dict, Any
import json
import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    encoding="utf-8",
    decode_responses=True,
    protocol=2,
)

AUTH_KEY_PREFIX = "auth"
USER_KEY_PREFIX = "user"


def _token_key(token: str, token_type: str) -> str:
    return f"{AUTH_KEY_PREFIX}:{token_type}:{token}"


def _user_key(user_id: int) -> str:
    return f"{USER_KEY_PREFIX}:{user_id}"


async def store_token(token: str, user_id: int, token_type: str, ttl_seconds: int) -> None:
    key = _token_key(token, token_type)
    await redis_client.set(key, str(user_id), ex=ttl_seconds)


async def get_user_id_from_token(token: str, token_type: str) -> Optional[int]:
    key = _token_key(token, token_type)
    value = await redis_client.get(key)
    if value is None:
        return None
    return int(value)


async def delete_token(token: str, token_type: str) -> None:
    key = _token_key(token, token_type)
    await redis_client.delete(key)


async def delete_user_tokens(user_id: int) -> None:
    pattern = f"{AUTH_KEY_PREFIX}:*"
    async for key in redis_client.scan_iter(match=pattern):
        value = await redis_client.get(key)
        if value and int(value) == user_id:
            await redis_client.delete(key)


async def store_user(user_id: int, user_data: Dict[str, Any], ttl_seconds: int) -> None:
    key = _user_key(user_id)
    await redis_client.set(key, json.dumps(user_data, default=str), ex=ttl_seconds)


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    key = _user_key(user_id)
    value = await redis_client.get(key)
    if value is None:
        return None
    return json.loads(value)


async def delete_user(user_id: int) -> None:
    key = _user_key(user_id)
    await redis_client.delete(key)