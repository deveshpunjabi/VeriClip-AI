"""
API Dependencies for VeriClip AI.
Auth, rate limiting, and Pub/Sub publisher.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """
    Extract and validate the current user from the authorization header.
    TODO: Implement JWT validation and Firebase Auth integration.
    """
    if not credentials:
        # For MVP: Allow unauthenticated access
        return {"user_id": "anonymous", "role": "viewer"}
    
    # TODO: Validate JWT token
    # from firebase_admin import auth
    # token = auth.verify_id_token(credentials.credentials)
    
    return {"user_id": "authenticated_user", "role": "admin"}


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Require admin role for sensitive operations."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user


class RateLimiter:
    """Simple rate limiter (TODO: Replace with Redis-based limiter)."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def __call__(self, user: dict = Depends(get_current_user)):
        # TODO: Implement actual rate limiting
        return True


rate_limiter = RateLimiter()
