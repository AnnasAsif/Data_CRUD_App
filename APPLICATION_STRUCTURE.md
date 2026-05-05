# Application Structure & Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  Web Browser          │  Mobile App       │  API Client      │
│  (HTML/JS/CSS)        │  (REST API)       │  (cURL/Python)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Routes (routes.py)                                  │
│  ├─ Web UI Routes (/api/crud/ui/*)                          │
│  ├─ Project Routes (/api/crud/*_project)                    │
│  ├─ Category Routes (/api/crud/*_categor*)                  │
│  └─ Asset Routes (/api/crud/*_asset)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      MIDDLEWARE LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Authentication Middleware (auth_middleware.py)              │
│  ├─ API Key Validation                                       │
│  ├─ Protected Path Checking                                  │
│  └─ Request State Management                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       BUSINESS LOGIC                         │
├─────────────────────────────────────────────────────────────┤
│  Controller (controller/controller.py)                       │
│  ├─ Project Management                                       │
│  ├─ Category Management                                      │
│  ├─ Asset Management                                         │
│  └─ Custom Fields Management                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       UTILITY LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  Utils (utils/)                                              │
│  ├─ File Operations (functions.py)                           │
│  ├─ Image Processing (preprocess_image.py)                   │
│  └─ Thumbnail Generation (postprocess_image.py)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA ACCESS LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  Database Config (database/database_config.py)               │
│  ├─ MongoDB Connection                                       │
│  └─ Database Getters                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  MongoDB                                                     │
│  ├─ assets_db                                                │
│  │   ├─ projects (collection)                                │
│  │   ├─ category_{project_name} (collections)               │
│  │   └─ assets_{project_name} (collections)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       FILE STORAGE                           │
├─────────────────────────────────────────────────────────────┤
│  static/                                                     │
│  ├─ {project_name}/                                          │
│  │   ├─ Original/                                            │
│  │   │   ├─ Category/ (category images)                     │
│  │   │   └─ Asset/                                           │
│  │   │       └─ {category_name}/                             │
│  │   │           └─ {asset_name}/ (asset files)             │
│  │   └─ Thumbnail/                                           │
│  │       ├─ Category/ (category thumbnails)                 │
│  │       └─ Asset/                                           │
│  │           └─ {category_name}/                             │
│  │               └─ {asset_name}/ (asset thumbnails)        │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Creating a Project

```
User Input (Web UI/API)
    │
    ├─ projectName: "My Sticker App"
    ├─ assetType: "sticker"
    └─ projectImage: <file>
    │
    ▼
routes.py: create_project()
    │
    ├─ Validate input
    ├─ Check API key
    └─ Set request state
    │
    ▼
controller.py: create_project()
    │
    ├─ Check if project exists
    ├─ Create folder structure:
    │   ├─ static/my_sticker_app/
    │   ├─ static/my_sticker_app/Original/Category/
    │   ├─ static/my_sticker_app/Original/Asset/
    │   ├─ static/my_sticker_app/Thumbnail/Category/
    │   └─ static/my_sticker_app/Thumbnail/Asset/
    ├─ Save project image
    ├─ Generate thumbnail
    └─ Create Project model
    │
    ▼
MongoDB: Insert into projects collection
    │
    ▼
Response: {"Message": "My Sticker App - Project Created"}
```

### Creating a Category

```
User Input
    │
    ├─ projectName: "My Sticker App"
    ├─ assetType: "sticker"
    └─ categories: ["Animals", "Food"]
    │
    ▼
routes.py: add_categories()
    │
    ▼
controller.py: add_categories()
    │
    ├─ For each category:
    │   ├─ Check if exists
    │   ├─ Create folders:
    │   │   ├─ static/my_sticker_app/Original/Asset/animals/
    │   │   └─ static/my_sticker_app/Thumbnail/Asset/animals/
    │   └─ Create Category model
    │
    ▼
MongoDB: Insert into category_my_sticker_app collection
    │
    ▼
Response: {"message": "2 Categories Created"}
```

### Creating an Asset

```
User Input
    │
    ├─ projectName: "My Sticker App"
    ├─ categoryId: "abc123"
    ├─ categoryName: "Animals"
    ├─ name: "Cute Cat"
    ├─ image: cat.gif
    └─ thumbnail: cat_thumb.png (optional)
    │
    ▼
routes.py: create_asset()
    │
    ▼
controller.py: add_new_asset()
    │
    ├─ Check if asset exists
    ├─ Create folders:
    │   ├─ static/my_sticker_app/Original/Asset/animals/cute_cat/
    │   └─ static/my_sticker_app/Thumbnail/Asset/animals/cute_cat/
    ├─ Save image file
    ├─ Save/generate thumbnail
    └─ Create Asset model
    │
    ▼
MongoDB: Insert into assets_my_sticker_app collection
    │
    ▼
Response: {"message": "Cute Cat asset added in category Animals"}
```

## Web UI Flow

### User Journey

```
1. Dashboard (index.html)
   │
   ├─ Click "Manage Projects"
   │   │
   │   ▼
   │   2. Projects Page (projects.html)
   │      │
   │      ├─ View all projects
   │      ├─ Create new project
   │      ├─ Edit project
   │      ├─ Delete project
   │      │
   │      └─ Click "View Categories"
   │          │
   │          ▼
   │          3. Categories Page (categories.html)
   │             │
   │             ├─ View categories for project
   │             ├─ Create categories
   │             ├─ Edit category
   │             ├─ Delete category
   │             │
   │             └─ Click "View Assets"
   │                 │
   │                 ▼
   │                 4. Assets Page (assets.html)
   │                    │
   │                    ├─ View assets for category
   │                    ├─ Create asset
   │                    ├─ Edit asset
   │                    ├─ Add custom fields
   │                    └─ Delete asset
```

## API Request Flow

### Example: Create Asset with Custom Fields

```
Step 1: Create Asset
POST /api/crud/create_asset
    │
    ├─ Headers: X-API-Key: your-secret-api-key
    ├─ Body (multipart/form-data):
    │   ├─ projectName: "My App"
    │   ├─ categoryId: "cat123"
    │   ├─ categoryName: "Videos"
    │   ├─ name: "Funny Video"
    │   ├─ image: video.mp4
    │   ├─ thumbnail: thumb.jpg
    │   ├─ isEnable: true
    │   └─ isPremium: false
    │
    ▼
Response: {"message": "Funny Video asset added in category Videos"}
    │
    ▼
Step 2: Add Custom Fields
PUT /api/crud/addMoreFields
    │
    ├─ Headers: X-API-Key: your-secret-api-key
    ├─ Body (multipart/form-data):
    │   ├─ projectName: "My App"
    │   ├─ categoryName: "Videos"
    │   ├─ assetName: "Funny Video"
    │   ├─ assetId: "asset123"
    │   ├─ key0: "background_music"
    │   ├─ value0: music.mp3
    │   ├─ key1: "subtitle"
    │   └─ value1: subtitle.srt
    │
    ▼
Response: {"message": "Successfully added/updated 2 field(s) in moreFields"}
```

## File Organization

### Project Structure on Disk

```
static/
├── no_image.jpg (default image)
├── no_thumbnail.jpg (default thumbnail)
│
├── my_sticker_app/
│   ├── project_image.jpg
│   ├── thumb_project_image.jpg
│   │
│   ├── Original/
│   │   ├── Category/
│   │   │   ├── animals.png
│   │   │   └── food.png
│   │   │
│   │   └── Asset/
│   │       ├── animals/
│   │       │   ├── cute_cat/
│   │       │   │   ├── cat.gif
│   │       │   │   └── cat_sound.mp3 (custom field)
│   │       │   └── funny_dog/
│   │       │       └── dog.gif
│   │       │
│   │       └── food/
│   │           └── pizza/
│   │               └── pizza.png
│   │
│   └── Thumbnail/
│       ├── Category/
│       │   ├── animals.png
│       │   └── food.png
│       │
│       └── Asset/
│           ├── animals/
│           │   ├── cute_cat/
│           │   │   └── cat.gif
│           │   └── funny_dog/
│           │       └── dog.gif
│           │
│           └── food/
│               └── pizza/
│                   └── pizza.png
│
└── video_effects_app/
    └── (similar structure)
```

## Database Schema

### Collections Structure

```
assets_db (database)
│
├── projects (collection)
│   └── Document:
│       ├── _id: ObjectId
│       ├── name: "My Sticker App"
│       ├── asset_type: "sticker"
│       ├── image_url: "http://..."
│       ├── thumbnail_url: "http://..."
│       ├── created_at: DateTime
│       └── updated_at: DateTime
│
├── category_my_sticker_app (collection)
│   └── Document:
│       ├── _id: ObjectId
│       ├── name: "Animals"
│       ├── asset_type: "sticker"
│       ├── is_enabled: true
│       ├── is_premium: false
│       ├── sequence: 0
│       ├── image_url: "http://..."
│       ├── thumbnail_url: "http://..."
│       ├── created_at: DateTime
│       └── updated_at: DateTime
│
└── assets_my_sticker_app (collection)
    └── Document:
        ├── _id: ObjectId
        ├── category_id: "cat123"
        ├── name: "Cute Cat"
        ├── description: null
        ├── image_url: "http://..."
        ├── thumbnail_url: "http://..."
        ├── is_enabled: true
        ├── is_premium: false
        ├── sequence: 0
        ├── views: 0
        ├── downloads: 0
        ├── moreFields: {
        │   "background_music": "http://.../music.mp3",
        │   "subtitle": "http://.../subtitle.srt"
        │   }
        ├── created_at: DateTime
        └── updated_at: DateTime
```

## Security Flow

```
Client Request
    │
    ▼
Is path protected?
    │
    ├─ NO → Process request
    │
    └─ YES → Check API Key
        │
        ├─ Valid → Process request
        │
        └─ Invalid → Return 403 Forbidden
```

## Error Handling

```
Request
    │
    ▼
Try:
    ├─ Validate input
    ├─ Check permissions
    ├─ Process business logic
    ├─ Database operations
    └─ File operations
    │
    ▼
Catch Exception:
    ├─ ValueError → 400 Bad Request
    ├─ HTTPException → Custom status code
    └─ Other → 500 Internal Server Error
    │
    ▼
Return JSON Response:
    ├─ Success: {"message": "..."}
    └─ Error: {"status": "error", "message": "...", "detail": "..."}
```

## Performance Considerations

1. **Database Indexing**: Consider adding indexes on frequently queried fields
2. **File Storage**: Use CDN for production deployments
3. **Thumbnail Generation**: Async processing for large files
4. **Caching**: Implement Redis for frequently accessed data
5. **Connection Pooling**: MongoDB connection pool already configured

## Scalability

```
Current Setup (Single Server)
    │
    ▼
Horizontal Scaling Options:
    │
    ├─ Load Balancer
    │   ├─ App Server 1
    │   ├─ App Server 2
    │   └─ App Server 3
    │
    ├─ Shared File Storage (NFS/S3)
    │
    └─ MongoDB Replica Set
```

---

This structure provides a clear, maintainable, and scalable foundation for your asset management system!
