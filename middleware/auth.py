import os
from typing import Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database.db import get_db
from services.activity_service import log_user_activity

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "your-auth0-domain.auth0.com")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE", "your-api-identifier")
ALGORITHMS = ["RS256"]

security = HTTPBearer()


class Auth0Error(Exception):
    """Custom exception for Auth0 errors."""


def get_token_from_header(credentials: HTTPAuthorizationCredentials) -> str:
    """Extract token from Authorization header."""
    if not credentials or not credentials.scheme == "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Expected 'Bearer'.",
        )
    return credentials.credentials


def verify_token(token: str) -> Dict:
    """Verify Auth0 JWT token."""
    try:
        # Get Auth0 public key
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        import requests
        
        response = requests.get(jwks_url)
        jwks = response.json()
        
        # Get the unverified header
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the key
        rsa_key = None
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if rsa_key is None:
            raise Auth0Error("Unable to find a valid signing key")
        
        # Verify the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return payload
        
    except JWTError as e:
        raise Auth0Error(f"Invalid token: {str(e)}")
    except Exception as e:
        raise Auth0Error(f"Token verification failed: {str(e)}")


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = security,
    db: Session = next(get_db())
) -> Dict:
    """Get current authenticated user from token."""
    try:
        token = get_token_from_header(credentials)
        payload = verify_token(token)
        
        # Extract user information
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise Auth0Error("User ID not found in token")
        
        # Log the activity
        log_user_activity(
            db=db,
            user_id=user_id,
            user_email=email,
            action="API_ACCESS",
            endpoint=str(request.url.path),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            status="SUCCESS"
        )
        
        return {
            "user_id": user_id,
            "email": email,
            "payload": payload
        }
        
    except Auth0Error as e:
        # Log failed access attempt
        log_user_activity(
            db=db,
            user_id="unknown",
            action="API_ACCESS_FAILED",
            endpoint=str(request.url.path),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            status="FAILED",
            details=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# Public endpoints that don't require authentication
PUBLIC_ENDPOINTS = {
    "/api/docs",
    "/api/redoc", 
    "/api/openapi.json",
    "/user/signup",
    "/user/signin",
    "/user/profile/view",
    "/user/profile/update",
    "/user/change-password",
    "/profile"
}


def is_public_endpoint(request: Request) -> bool:
    """Check if the endpoint is public (doesn't require authentication)."""
    path = str(request.url.path)
    return path in PUBLIC_ENDPOINTS or path.startswith("/static/")
