import os
from environment import config
from analytics.excluded_paths import EXCLUDE_PATHS
from analytics.middleware import AnalyticsMiddleware
from utils.auth_middleware import AuthorizationMiddleware
from routes import router
from analytics.routes import router as analytics_router

#Server Initialization
from inits.server_init import app

#Setup Authorization Middleware
# Define paths that require authorization (create/edit operations)
PROTECTED_PATHS = [
    "/api/crud/create_new_project",
    "/api/crud/edit_project",
    "/api/crud/add_categories",
    "/api/crud/add_assets",
    "/api/crud/updateAsset"
]

app.add_middleware(
    AuthorizationMiddleware,
    protected_paths=PROTECTED_PATHS,
    api_key=os.getenv("API_KEY", "your-secret-api-key")
)

#Setup Analytics Router
app.add_middleware(
    AnalyticsMiddleware,
    exclude_paths=EXCLUDE_PATHS
    )

#Add routers
app.include_router(router)                      #Assets Router
app.include_router(analytics_router)            #Analytics Router

#============================================================================
