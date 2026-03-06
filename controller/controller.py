import os
import shutil
from bson import ObjectId
from datetime import datetime

from utils.preprocess_image import create_thumbnail

#loading database functions
from database.database_config import get_assets_db
from database.assets_model import Category, Asset
from database.project_model import Project

from utils.functions import create_target_Assets_folders, save_files_by_folder,save_single_file_by_folder, create_req_folder, rename_folder

from environment import config

from fastapi import HTTPException
#=======================================================================================
#=======================================================================================
#=======================================================================================
#Function to create new Project Instance
async def create_project(
    projectName,
    projectImage
):
    try:
        db = get_assets_db()
        collection = db[config.PROJECTS_COLLECTION]

        image_url= config.DEFAULT_IMAGE
        thumbnail_url= config.DEFAULT_THUMBNAIL
        foldername= projectName.replace(" ","_").lower()

        # Finding if alread exists
        condition = {"name": projectName}
        projection = {}
        projects = await collection.find(condition, projection).to_list(length=None)
        if len(projects) > 0:

            raise ValueError("This Project Already Exists")

        project_path = f"{config.STATIC_DIR}/{foldername}"
        create_req_folder(project_path)
        #original folders for Category and Asset
        create_req_folder(f"{project_path}/Original")
        create_req_folder(f"{project_path}/Original/Category")
        create_req_folder(f"{project_path}/Original/Asset")
        #thumbnail folders for Category and Asset
        create_req_folder(f"{project_path}/Thumbnail")
        create_req_folder(f"{project_path}/Thumbnail/Category")
        create_req_folder(f"{project_path}/Thumbnail/Asset")

        if projectImage:
            print("Image found")
            filename = projectImage.filename
            filepath = f"{project_path}/{filename}"
            thumbnailpath = f"{project_path}/thumb_{filename}"

            #Save image
            await save_single_file_by_folder(project_path, projectImage)
            #Save thumbnail
            await create_thumbnail(filepath, thumbnailpath)

            image_url= f"{config.FILE_URL_PREFIX}/{project_path}/{filename}"
            thumbnail_url= f"{config.FILE_URL_PREFIX}/{project_path}/thumb_{filename}"

        print(image_url)
        project_model = Project(
            name = projectName,
            image_url = image_url,
            thumbnail_url = thumbnail_url
        )
        await collection.insert_one(project_model.model_dump())

        return {
            "Message": f"{projectName} - Project Created"
        }
    except Exception as e:
        print(e)
        raise HTTPException (
            status_code=500,
            detail=f"Failed to add project: {e}"
        )

#=================================================
#Get list of projects
async def get_projects(
):
    try:
        db = get_assets_db()
        collection = db[config.PROJECTS_COLLECTION]

        condition = {}
        projection = {}
        projects = await collection.find(condition, projection).to_list(length=None)

        # 2. Convert ObjectId to string for every document
        for project in projects:
            project["_id"] = str(project["_id"])

        return {
            "projects": projects,
            "message": f"{len(projects)} - returned"
        }
    except Exception as e:
        print(e)
        raise HTTPException (
            status_code=500,
            detail=f"Failed to add categories: {e}"
        )

#=================================================
#Update a project
async def update_project(
    projectName,
    projectImage,
    newprojectName
):
    try:
        db = get_assets_db()
        collection = db[config.PROJECTS_COLLECTION]
        if newprojectName:
            name = newprojectName
        else:
            name = projectName
        
        foldername = projectName.replace(" ","_").lower()
        folderfullpath = f"{config.STATIC_DIR}/{foldername}"

        newfoldername = newprojectName.replace(" ","_").lower()
        if newfoldername:
            newfolderfullpath = f"{config.STATIC_DIR}/{newfoldername}"
        
        image_url= None
        thumbnail_url= None

        if projectImage:
            print("Image Loaded")
            filename = projectImage.filename
            imagepath = f"{folderfullpath}/{filename}"
            thumbnailpath = f"{folderfullpath}/thumb_{filename}"

            #Save image
            await save_single_file_by_folder(folderfullpath, projectImage)
            #Save thumbnail
            await create_thumbnail(imagepath, thumbnailpath)

            image_url = f"{config.FILE_URL_PREFIX}/{imagepath}"
            image_url = f"{config.FILE_URL_PREFIX}/{thumbnailpath}"

        if newfoldername:
            rename_folder(folderfullpath, newfolderfullpath)
            
        #model for updation
        project_model = Project(
            name= name,
            updated_at = datetime.utcnow()
        )

        if image_url is not None:
            project_model.image_url = image_url
        if thumbnail_url is not None:
            project_model.thumbnail_url = thumbnail_url

        filter_criteria = {"name": projectName}
        update_data = {"$set": project_model.model_dump(exclude_unset=True)}
        await collection.update_one(filter_criteria, update_data)

        return {
            "Message": f"{name} project updated"
        }


    except Exception as e:
        print(e)
        raise HTTPException(
            status_code = 500,
            detail = f"Failed to update project : {e}"
        )

#=================================================
#Delete a complete project alongwith Categories and Assets
async def remove_project(
    projectName
):
    project_name = projectName.replace(" ", "_").lower()
    db = get_assets_db()
    collection = db[config.PROJECTS_COLLECTION]
    categories_collection = db[f"{config.CATEGORIES_COLLECTION}_{project_name}"]
    assets_collection = db[f"{config.ASSETS_COLLECTION}_{project_name}"]

    try:
        # Delete project folder and all its contents
        project_folder_path = f"{config.STATIC_DIR}/{project_name}"
        if os.path.exists(project_folder_path):
        
            shutil.rmtree(project_folder_path)
        
        # Delete project document from projects collection
        await collection.delete_one({"name": projectName})
        
        # Delete all categories for this project
        await categories_collection.drop()
        
        # Delete all assets for this project
        await assets_collection.drop()
        
        return {
            "Message": f"{projectName} project and all associated data deleted successfully"
        }
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete project: {e}"
        )
    

#=======================================================================================
#=======================================================================================
#Add a new category
async def add_categories(
    categories, 
    projectName,
    images, 
    has_images
):
    try:
        project_foldername = projectName.replace(" ","_").lower()
        db = get_assets_db()
        collection = db[f"{config.CATEGORIES_COLLECTION}_{project_foldername}"]

        category_folder = f"{config.STATIC_DIR}/{project_foldername}/Original/Category"
        cat_thumbnail_folder = f"{config.STATIC_DIR}/{project_foldername}/Thumbnail/Category"
        
        if has_images:
            # Images Recieved
            print("Images Recieved")
            await save_files_by_folder(category_folder, images)

            created_count = 0
            for image in images:
                filename = image.filename
                category = filename.split(".")[0]
                
                # Check if category already exists
                existing = await collection.find_one({"name": category})
                if existing:
                    print(f"Category '{category}' already exists, skipping")
                    continue
                
                filepath = f"{category_folder}/{filename}"
                thumbnailpath = f"{cat_thumbnail_folder}/{filename}"

                #create thumbnail and make url
                await create_thumbnail(filepath, thumbnailpath)
                image_url = f"{config.FILE_URL_PREFIX}/{filepath}"
                thumbnail_url = f"{config.FILE_URL_PREFIX}/{thumbnailpath}"

                #create folder by category name for assets
                create_req_folder(f"{category_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}")
                #create folder by category name for assets thumbnails
                create_req_folder(f"{cat_thumbnail_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}")
                
                category_model = Category(
                    name= category,
                    image_url= image_url,
                    thumbnail_url= thumbnail_url
                )

                await collection.insert_one(category_model.model_dump())
                created_count += 1
            return {
                "message": f"{created_count} Categories Created using images"
            }
        else:
            # Categories Recieved
            print("Categories Recieved")
            created_count = 0
            for category in categories:
                # Check if category already exists
                existing = await collection.find_one({"name": category})
                if existing:
                    print(f"Category '{category}' already exists, skipping")
                    continue
                
                category_model = Category(
                    name=category,
                    image_url= config.DEFAULT_IMAGE,
                    thumbnail_url= config.DEFAULT_THUMBNAIL
                )

                #create folder for assets
                create_req_folder(f"{category_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}")
                #create folder for assets thumbnails
                create_req_folder(f"{cat_thumbnail_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}")

                await collection.insert_one(category_model.model_dump())
                created_count += 1
            return {
                "message": f"{created_count} Categories Created"
            }

    except Exception as e:
        print(e)
        raise HTTPException (
            status_code=500,
            detail=f"Failed to add categories: {e}"
        )

#=================================================
# Update an existing Category
async def update_category(
    projectName,
    categoryId,
    categoryName,
    image,
    isEnable,
    isPremium
):
    try:
        project_foldername = projectName.replace(" ","_").lower()

        db = get_assets_db()
        collection = db[f"{config.CATEGORIES_COLLECTION}_{project_foldername}"]


        old_cat = await collection.find_one({"_id": ObjectId(categoryId)})
        if old_cat:
            old_categoryName = old_cat.get("name").replace(" ","_").lower()
        else:
            raise ValueError("No such category found")
            # Handle the "Not Found" case here
        Category_Name = old_categoryName

        # Category and Thumbnail Static folders if required
        category = old_categoryName
        category_folder = f"{config.STATIC_DIR}/{project_foldername}/Original/Category"
        cat_thumbnail_folder = f"{config.STATIC_DIR}/{project_foldername}/Thumbnail/Category"

        # If new category name is provided
        if categoryName is not None:
            category = categoryName
            Category_Name = categoryName

            # New Folder paths
            new_AssetsFolder = f"{category_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}"
            new_Assets_thumbnails = f"{cat_thumbnail_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}"
            # Old Folder Paths
            old_AssetsFolder = f"{category_folder.replace("Category","Asset")}/{old_categoryName}"
            old_Assets_thumbnails = f"{cat_thumbnail_folder.replace("Category","Asset")}/{old_categoryName}"

            # Renaming folders
            rename_folder(old_AssetsFolder, new_AssetsFolder)
            rename_folder(old_Assets_thumbnails, new_Assets_thumbnails)
        
        image_url= None
        thumbnail_url= None
        if image:
            print('image found')
            filename = image.filename
            category = filename.split(".")[0]
            Category_Name = category
            filepath = f"{category_folder}/{filename}"
            thumbnailpath = f"{cat_thumbnail_folder}/{filename}"

            await save_single_file_by_folder(category_folder, image)

            #create thumbnail and make url
            await create_thumbnail(filepath, thumbnailpath)
            image_url = f"{config.FILE_URL_PREFIX}/{filepath}"
            thumbnail_url = f"{config.FILE_URL_PREFIX}/{thumbnailpath}"

        category_model = Category(
            name= Category_Name,
            updated_at = datetime.utcnow()
        )

        if image_url is not None:
            category_model.image_url = image_url
        if thumbnail_url is not None:
            category_model.thumbnail_url = thumbnail_url

        if isEnable is not None:
            category_model.is_enabled = str(isEnable).lower() == "true"
        if isPremium is not None:
            category_model.is_premium = str(isPremium).lower() == "true"

        filter_criteria = {"_id": ObjectId(categoryId)}
        update_data = {"$set": category_model.model_dump(exclude_unset=True)}

        await collection.update_one(filter_criteria, update_data)

        return {
            "message": f"Category '{category}' Updated"
        }

    except Exception as e:
        print(e)
        raise HTTPException (
            status_code=500,
            detail=f"Failed to update category: {e}"
        )

#=================================================
#Read all the categories
async def get_all_categories(
    projectName,
    isAdmin
):
    try:
        project_foldername = projectName.replace(" ","_").lower()
        db = get_assets_db()
        collection = db[f"{config.CATEGORIES_COLLECTION}_{project_foldername}"]
        
        condition = {}
        projection = {}
        
        if not isAdmin or isAdmin == "false":
            condition = {
                "is_enabled": True
                }
            projection = {
                "sequence": 0,
                "is_enabled": 0,
                "created_at": 0,
                "updated_at": 0
            }
        print(condition)
        # 1. Fetch the data
        categories = await collection.find(condition,projection).to_list(length=None)
        
        # 2. Convert ObjectId to string for every document
        for category in categories:
            category["_id"] = str(category["_id"])
        return {
            "categories": categories,
            "message": f"{len(categories)} categories found"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {e}"
        )

#=================================================
#Delete a catgory and it's assets
async def remove_category(
    projectName, 
    categoryId
):
    try:
        project_name = projectName.replace(" ", "_").lower()
        db = get_assets_db()
        # reading collections for deletion
        categories_collection = db[f"{config.CATEGORIES_COLLECTION}_{project_name}"]
        assets_collection = db[f"{config.ASSETS_COLLECTION}_{project_name}"]

        #Find category instance for name reading
        match_category = await categories_collection.find_one({"_id": ObjectId(categoryId)})
        if match_category is None:
            raise ValueError("Category Doesn't Exist")

        category_Name = match_category.get("name")
        category_Folder = category_Name.replace(" ","_").lower()

        # Delete category folder and all its contents from Original/Asset and Thumbnail/Asset
        original_category_path = f"{config.STATIC_DIR}/{project_name}/Original/Asset/{category_Folder}"
        thumbnail_category_path = f"{config.STATIC_DIR}/{project_name}/Thumbnail/Asset/{category_Folder}"
        

        if os.path.exists(original_category_path):
            shutil.rmtree(original_category_path)
        if os.path.exists(thumbnail_category_path):
            shutil.rmtree(thumbnail_category_path)
        
        # Delete category document from categories collection
        await categories_collection.delete_one({"_id": ObjectId(categoryId)})
        
        # Delete all assets for this category
        await assets_collection.delete_many({"category_id": categoryId})
        
        
        
        return {
            "Message": f"{category_Name} - category and it's assets deleted successfully"
        }
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete category: {e}"
        )
 

#=======================================================================================
#=======================================================================================

# Add a new asset
async def add_new_asset(
    projectName,
    categoryId,
    categoryName,
    name,
    image,
    thumbnail,
    isPremium,
    isEnable,
    sequence
):
    try:
        # Names modified for folder reading
        projectName_modified = projectName.replace(" ","_").lower()
        categoryName_modified = categoryName.replace(" ","_").lower()
        name_modified = name.replace(" ","_").lower()

        # setting up collection
        db = get_assets_db()
        collection = db[f"{config.ASSETS_COLLECTION}_{projectName_modified}"]
        # Check if asset already existing
        condition = {"category_id": categoryId, "name": name}
        existing = await collection.find_one(condition)
        if existing:
            raise ValueError("Asset already exists")

        #folder to store image
        image_folderpath = f"static/{projectName_modified}/Original/Asset/{categoryName_modified}/{name_modified}"
        os.makedirs(image_folderpath, exist_ok=True)
        #folder to store thumbnail
        thumbnail_folderpath = f"static/{projectName_modified}/Thumbnail/Asset/{categoryName_modified}/{name_modified}"
        os.makedirs(thumbnail_folderpath, exist_ok=True)

        image_url = config.DEFAULT_IMAGE
        thumbnail_url = None

        # logic for creating thumbnail
        if thumbnail:
            # write thumbnail logic here
            await save_single_file_by_folder(category_folderpath, thumbnail)

            thumbnail_url = f"{config.FILE_URL_PREFIX}/static/{projectName_modified}/Thumbnail/Asset/{categoryName_modified}/{name_modified}/{thumbnail.filename}"


        if image:
            # write image logic here
            filename= image.filename

            await save_single_file_by_folder(image_folderpath, image)

            image_url = f"{config.FILE_URL_PREFIX}/static/{projectName_modified}/Original/Asset/{categoryName_modified}/{name_modified}/{filename}"

            
            # create a thumbnail
            if thumbnail_url is None:
                await create_thumbnail(f"{image_folderpath}/{filename}", f"{thumbnail_folderpath}/{filename}")

                thumbnail_url = f"{config.FILE_URL_PREFIX}/static/{projectName_modified}/Thumbnail/Asset/{categoryName_modified}/{name_modified}/{filename}"

        if thumbnail_url is None:
            thumbnail_url = config.DEFAULT_THUMBNAIL
        
        asset_model = Asset(
            category_id= categoryId,
            name= name,
            image_url= image_url,
            thumbnail_url= thumbnail_url,
            moreFields= {}
        )
        if isEnable:
            asset_model.is_enabled = str(isEnable).lower() == "true"
        if isPremium:
            asset_model.is_premium = str(isPremium).lower() == "true"
        if sequence:
            asset_model.sequence = int(sequence)

        await collection.insert_one(asset_model.model_dump())
        return {
            "message": f"{name} asset added in category {categoryName}"
        }


    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= f"Error while Creating the Asset"
        )

#=================================================

async def get_assets(
    categoryId,
    projectName,
    isAdmin
):
    try:
        db = get_assets_db()
        projectName_modified= projectName.replace(" ","_").lower()
        
        collection = db[f"{config.ASSETS_COLLECTION}_{projectName_modified}"]

        condition = {}
        projection = {}
        
        if categoryId:
            condition["category_id"] = categoryId
        if not isAdmin:
            condition["is_enabled"] = True

        assets = await collection.find(condition, projection).to_list(length=None)

        for asset in assets:
            asset["_id"] = str(asset["_id"])
        
        return {
            "assets": assets,
            "message": f"{len(assets)} assets retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve assets: {e}"
        )

#=================================================

async def remove_asset(
    projectName,
    categoryName,
    assetName,
    assetId
):
    projectName_modified = projectName.replace(" ","_").lower()
    categoryName_modified = categoryName.replace(" ","_").lower()
    assetName_modified = assetName.replace(" ","_").lower()

    try:
        db = get_assets_db()
        collection = db[f"{config.ASSETS_COLLECTION}_{projectName_modified}"]

        # folders to be deleted
        original_folder =f"static/{projectName_modified}/Original/Asset/{categoryName_modified}/{assetName_modified}"
        thumbnail_folder =f"static/{projectName_modified}/Thumbnail/Asset/{categoryName_modified}/{assetName_modified}"

        if os.path.exists(original_folder):
            shutil.rmtree(original_folder)
        if os.path.exists(thumbnail_folder):
            shutil.rmtree(thumbnail_folder)
        
        # Delete category document from categories collection
        await collection.delete_one({
            "_id": ObjectId(assetId)
        })

        return {
            "Message": f"{assetName} - asset deleted successfully"
        }
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete Asset: {e}"
        )

#=================================================

async def update_asset(
    projectName,
    categoryName,
    assetName,
    assetId,
    assetNewName,
    image,
    thumbnail,
    isEnable, 
    isPremium,
    sequence,
    views
):
    try:
        projectName_modified  = projectName.replace(" ","_").lower()
        categoryName_modified = categoryName.replace(" ","_").lower()
        assetName_modified    = assetName.replace(" ","_").lower()

        db = get_assets_db()
        collection = db[f"{config.ASSETS_COLLECTION}_{projectName_modified}"]

        name = assetName
        assetPath = f"static/{projectName_modified}/Original/Asset/{categoryName_modified}/{assetName_modified}"
        thumbnailPath = f"static/{projectName_modified}/Thumbnail/Asset/{categoryName_modified}/{assetName_modified}"

        obj={}
        #Setting up New Name and rename the folders
        if assetNewName:
            assetNewName_modified = assetNewName.replace(" ","_").lower()

            newAssetPath = f"static/{projectName_modified}/Original/Asset/{categoryName_modified}/{assetNewName_modified}"
            newThumbnailPath = f"static/{projectName_modified}/Thumbnail/Asset/{categoryName_modified}/{assetNewName_modified}"

            rename_folder(assetPath, newAssetPath)
            rename_folder(thumbnailPath, newThumbnailPath)

            #swith old values to new values
            name = assetNewName
            assetPath = newAssetPath
            thumbnailPath = newThumbnailPath
            #store in object
            obj["name"] = assetNewName

        image_url = None
        thumbnail_url = None

        # logic for creating thumbnail
        if thumbnail:
            await save_single_file_by_folder(thumbnailPath, thumbnail)

            thumbnail_url = f"{thumbnailPath}/{thumbnail.filename}"


        if image:
            filename= image.filename

            await save_single_file_by_folder(assetPath, image)

            image_url = f"{assetPath}/{filename}"

            
            # create a thumbnail
            if thumbnail_url is None:
                await create_thumbnail(f"{assetPath}/{filename}", f"{thumbnailPath}/{filename}")

                thumbnail_url = f"{thumbnailPath}/{filename}"

        if image_url:
            obj["image_url"] = config.FILE_URL_PREFIX +'/'+ image_url
        if thumbnail_url:
            obj["thumbnail_url"] = config.FILE_URL_PREFIX +'/'+  thumbnail_url
        if isEnable:
            obj["is_enabled"] = str(isEnable).lower() == "true"
        if isPremium:
            obj["is_premium"] = str(isPremium).lower() == "true"
        if sequence:
            obj["sequence"] = int(sequence)
        if views:
            obj["views"] = int(views)

        print(obj)

        await collection.update_one(
            {"_id": ObjectId(assetId)},
            {"$set": obj}
        )

        return {
            "Message": f"'{assetName}' - asset updated"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating the asset: {e}"
        )

#=================================================

async def increaseView(
    projectName,
    asset_id
):
    try:
        db = get_assets_db()

        projectName_modified = projectName.replace(" ","_").lower()

        collection = db[f"{config.ASSETS_COLLECTION}_{projectName_modified}"]

        condition = {"_id": ObjectId(asset_id)}            
        updateSet = {"$inc" : {"views": 1}}

        result = await collection.update_one(condition, updateSet)

        if result.matched_count == 0:
            return {"error": "Asset not found"}
        
        return {"message": "Views Count incremented"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update asset views-count: {e}"
        )