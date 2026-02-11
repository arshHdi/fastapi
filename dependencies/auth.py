from typing import Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from middleware.auth import get_current_user, is_public_endpoint

security = HTTPBearer()


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict]:
    """Get current user if token is provided, otherwise return None."""
    if is_public_endpoint(request):
        return None
    
    if not credentials:
        return None
    
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None


async def get_current_user_required(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    """Get current user - token is required."""
    if is_public_endpoint(request):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authentication not required for this endpoint"
        )
    
    return await get_current_user(request, credentials)
