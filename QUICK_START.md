# Quick Start Guide

## Getting Started in 5 Minutes

### 1. Start the Server

```bash
python run.py
```

The server will start at: `http://172.16.0.94:9006`

### 2. Access the Web UI

Open your browser and navigate to:
```
http://172.16.0.94:9006/api/crud/ui
```

### 3. Create Your First Project

1. Click on **"Manage Projects"**
2. Click **"+ Create New Project"**
3. Fill in:
   - **Project Name**: e.g., "My Sticker App"
   - **Asset Type**: Select "sticker" (or frame, suits, gif, etc.)
   - **Project Image**: Upload an optional image
4. Click **"Create Project"**

### 4. Add Categories

1. From the project card, click **"View Categories"**
2. Click **"+ Add Categories"**
3. Choose one method:
   - **Option A**: Enter category names manually (e.g., "Animals", "Food", "Nature")
   - **Option B**: Upload images (filename becomes category name)
4. Select the asset type if different from project default
5. Click **"Create Categories"**

### 5. Upload Assets

1. From a category card, click **"View Assets"**
2. Click **"+ Create Asset"**
3. Fill in:
   - **Asset Name**: e.g., "Cute Cat"
   - **Asset File**: Upload your file (.jpg, .png, .gif, .mp4, .mp3, etc.)
   - **Thumbnail**: Optional (auto-generated if not provided)
   - **Sequence**: Order number (default: 0)
   - Check **"Enabled"** to make it visible
   - Check **"Premium"** if it's a paid asset
4. Click **"Create Asset"**

### 6. Add Custom Fields (Optional)

For assets that need additional files (e.g., audio for a video, extra images):

1. From an asset card, click **"+ Fields"**
2. Enter field name (e.g., "audio", "background_music")
3. Upload the file
4. Click **"+ Add Field"** to add more
5. Click **"Save Custom Fields"**

## API Usage Example

### Using cURL

```bash
# Create a project
curl -X POST "http://172.16.0.94:9006/api/crud/create_new_project" \
  -H "X-API-Key: your-secret-api-key" \
  -F "projectName=My App" \
  -F "assetType=sticker" \
  -F "projectImage=@/path/to/image.jpg"

# Get all projects
curl "http://172.16.0.94:9006/api/crud/get_projects"

# Add categories
curl -X POST "http://172.16.0.94:9006/api/crud/add_categories" \
  -H "X-API-Key: your-secret-api-key" \
  -F "projectName=My App" \
  -F "assetType=sticker" \
  -F "categories=Animals" \
  -F "categories=Food"

# Create an asset
curl -X POST "http://172.16.0.94:9006/api/crud/create_asset" \
  -H "X-API-Key: your-secret-api-key" \
  -F "projectName=My App" \
  -F "categoryId=<category_id>" \
  -F "categoryName=Animals" \
  -F "name=Cute Cat" \
  -F "image=@/path/to/cat.gif" \
  -F "isEnable=true" \
  -F "isPremium=false"
```

### Using Python

```python
import requests

API_URL = "http://172.16.0.94:9006/api/crud"
API_KEY = "your-secret-api-key"

# Create a project
with open("project_image.jpg", "rb") as f:
    response = requests.post(
        f"{API_URL}/create_new_project",
        headers={"X-API-Key": API_KEY},
        data={
            "projectName": "My App",
            "assetType": "sticker"
        },
        files={"projectImage": f}
    )
    print(response.json())

# Get all projects
response = requests.get(f"{API_URL}/get_projects")
projects = response.json()["projects"]
print(f"Found {len(projects)} projects")

# Add categories
response = requests.post(
    f"{API_URL}/add_categories",
    headers={"X-API-Key": API_KEY},
    data={
        "projectName": "My App",
        "assetType": "sticker",
        "categories": ["Animals", "Food", "Nature"]
    }
)
print(response.json())

# Get categories
response = requests.get(
    f"{API_URL}/get_categories",
    params={"projectName": "My App", "isAdmin": "true"}
)
categories = response.json()["categories"]
category_id = categories[0]["_id"]

# Create an asset
with open("cat.gif", "rb") as f:
    response = requests.post(
        f"{API_URL}/create_asset",
        headers={"X-API-Key": API_KEY},
        data={
            "projectName": "My App",
            "categoryId": category_id,
            "categoryName": "Animals",
            "name": "Cute Cat",
            "isEnable": "true",
            "isPremium": "false",
            "sequence": "0"
        },
        files={"image": f}
    )
    print(response.json())
```

## Common Use Cases

### 1. Sticker App
- **Project**: "Sticker Pack App"
- **Asset Type**: "sticker"
- **Categories**: Emotions, Animals, Food, etc.
- **Assets**: PNG/WEBP images with transparent backgrounds

### 2. Frame App
- **Project**: "Photo Frame App"
- **Asset Type**: "frame"
- **Categories**: Birthday, Wedding, Holiday, etc.
- **Assets**: PNG frames with transparent centers

### 3. GIF Collection
- **Project**: "Animated GIF App"
- **Asset Type**: "gif"
- **Categories**: Funny, Reactions, Celebrations, etc.
- **Assets**: GIF files

### 4. Video Suits/Filters
- **Project**: "Video Effects App"
- **Asset Type**: "suits"
- **Categories**: Formal, Casual, Superhero, etc.
- **Assets**: Video files with custom fields for masks/overlays

## Tips & Best Practices

1. **Naming Convention**: Use clear, descriptive names for projects, categories, and assets
2. **Asset Types**: Choose appropriate asset types to organize your content
3. **Thumbnails**: Let the system auto-generate thumbnails for consistency
4. **Sequences**: Use sequence numbers to control display order (0, 10, 20, etc.)
5. **Enable/Disable**: Use the enabled flag to hide assets without deleting them
6. **Premium Content**: Mark premium assets to implement monetization
7. **Custom Fields**: Use custom fields for additional data like audio tracks, metadata, etc.
8. **File Formats**: 
   - Images: Use .webp for smaller file sizes
   - GIFs: Optimize before uploading
   - Videos: Use .mp4 with H.264 codec for best compatibility

## Troubleshooting

### Server won't start
- Check if MongoDB is running
- Verify port 9006 is not in use
- Check `.env` file configuration

### Can't upload files
- Verify API key in requests
- Check file size limits
- Ensure proper file permissions in `static/` directory

### Thumbnails not generating
- Verify Pillow and pillow-heif are installed
- Check image file format is supported
- Review server logs for errors

## Next Steps

- Explore the full API documentation in `README.md`
- Customize asset types in your project
- Integrate the API with your mobile/web app
- Set up analytics and tracking
- Implement user authentication for your app

## Support

For issues and questions, check the main `README.md` or contact the development team.
