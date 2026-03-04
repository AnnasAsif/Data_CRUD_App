#SYSTEM INFORMATION
SYSTEM_IP = "172.16.0.94"
SYSTEM_PORT = 9006

#PROJECT INFORMATION
APPNAME = "Data CRUD"
TITLE = "ALL ASSETS"
DESCRIPTION = "CRUD operations for Handling All assets, there are functions to add, retrieve, delete, and update assets and categories."
VERSION = "1.0.0"
AUTHOR = "Ozi Backend"

#MONGODB INFORMATION
MONGODB_URL = "mongodb://localhost:27017"
#BASE ANALYTICS DB and TABLE NAME
ANALYTICS_DATABASE = "analytics_db"
ANALYTICS_COLLECTION = f"analytics"
#BASE ASSETS DB and TABLE NAME
ASSETS_DATABASE = f"assets_db"
PROJECTS_COLLECTION = f"projects"
CATEGORIES_COLLECTION = f"category"
ASSETS_COLLECTION = f"assets"

#DIRECTORIES
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"

#FILE FORMATS
IMAGE_FORMAT = "webp"
TEMPLATE_FORMAT = "html"

#FILE PREFIX
FILE_URL_PREFIX = f"http://{SYSTEM_IP}:{SYSTEM_PORT}"

#DEFAULT VIEWS
DEFAULT_IMAGE = f"{FILE_URL_PREFIX}/static/no_image.jpg"
DEFAULT_THUMBNAIL = f"{FILE_URL_PREFIX}/static/no_thumbnail.jpg"