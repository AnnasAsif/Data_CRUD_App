import os
from environment import config
from analytics.excluded_paths import EXCLUDE_PATHS
from analytics.middleware import AnalyticsMiddleware
from routes import router
from analytics.routes import router as analytics_router

#Server Initialization
from inits.server_init import app

#Setup Analytics Router
app.add_middleware(
    AnalyticsMiddleware,
    exclude_paths=EXCLUDE_PATHS
    )

#Add routers
app.include_router(router)                      #Assets Router
app.include_router(analytics_router)            #Analytics Router

#============================================================================
