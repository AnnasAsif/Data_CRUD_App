import os
from environment import config
from utils.auth_middleware import AuthorizationMiddleware
from routes import router

#Server Initialization
from inits.server_init import app

#Setup Authorization Middleware
# Define paths that require authorization (create/edit operations)
from environment.protected_paths import PROTECTED_PATHS

app.add_middleware(
    AuthorizationMiddleware,
    protected_paths=PROTECTED_PATHS,
    api_key=os.getenv("API_KEY", "your-secret-api-key")
)

#Add routers
app.include_router(router)                      #Assets Router

#============================================================================
