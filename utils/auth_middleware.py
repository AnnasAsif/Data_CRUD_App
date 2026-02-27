from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os

class AuthorizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check authorization for protected endpoints.
    Validates API key or token for create/edit operations.
    """
    
    def __init__(self, app, protected_paths: list = None, api_key: str = None):
        super().__init__(app)
        self.protected_paths = protected_paths or []
        # Get API key from environment or use provided one
        self.api_key = api_key or os.getenv("API_KEY", "your-secret-api-key")
    
    async def dispatch(self, request: Request, call_next):
        # Check if the current path requires authorization
        if self._is_protected_path(request.url.path):
            # Validate authorization
            auth_result = self._validate_authorization(request)
            if not auth_result["authorized"]:
                return JSONResponse(
                    status_code=401,
                    content={
                        "status": "error",
                        "message": auth_result["message"]
                    }
                )
        
        # Continue with the request
        response = await call_next(request)
        return response
    
    def _is_protected_path(self, path: str) -> bool:
        """Check if the path requires authorization"""
        for protected_path in self.protected_paths:
            if protected_path in path:
                return True
        return False
    
    def _validate_authorization(self, request: Request) -> dict:
        """
        Validate authorization token/API key from request headers.
        Supports multiple auth methods:
        1. Bearer token in Authorization header
        2. API key in X-API-Key header
        """
        # Method 1: Check Authorization header (Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            if token == self.api_key:
                return {"authorized": True, "message": "Authorized"}
        
        # Method 2: Check X-API-Key header
        api_key_header = request.headers.get("X-API-Key")
        if api_key_header and api_key_header == self.api_key:
            return {"authorized": True, "message": "Authorized"}
        
        # No valid authorization found
        return {
            "authorized": False,
            "message": "Unauthorized: Missing or invalid API key"
        }
