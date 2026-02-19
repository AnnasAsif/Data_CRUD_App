import os
from bson import ObjectId

from utils.preprocess_image import create_thumbnail

#loading database functions
from database.database_config import get_assets_db
from database.assets_model import Category, Asset
from database.project_model import Project

from utils.functions import create_target_Assets_folders, save_files_by_folder,save_single_file_by_folder, create_req_folder

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

        image_url= None
        thumbnail_url= None
        foldername= projectName.replace(" ","_").lower()

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
            create_thumbnail(filepath, thumbnailpath)

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
            detail=f"Failed to add categories: {e}"
        )

#=======================================================================================
#Get list of projects
async def get_projects(
):
    try:
        db = get_assets_db()
        collection = db[config.PROJECTS_COLLECTION]

        condition = {}
        projection = {
            "created_at":0,
            "updated_at":0
        }
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

#=======================================================================================
#=======================================================================================

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

            for image in images:
                filename = image.filename
                category = filename.split(".")[0]
                filepath = f"{category_folder}/{filename}"
                thumbnailpath = f"{cat_thumbnail_folder}/{filename}"

                #create thumbnail and make url
                create_thumbnail(filepath, thumbnailpath)
                image_url = f"{config.IMAGE_URL_PREFIX}/{filepath}"
                thumbnail_url = f"{config.IMAGE_URL_PREFIX}/{thumbnailpath}"

                #create folder for assets
                create_req_folder(f"{category_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}")
                #create folder for assets thumbnails
                create_req_folder(f"{cat_thumbnail_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}")
                
                category_model = Category(
                    name= category,
                    projectName = projectName,
                    image_url= image_url,
                    thumbnail_url= thumbnail_url
                )

                await collection.insert_one(category_model.model_dump())
            return {
                "message": f"{len(images)} Categories Created using images"
            }
        else:
            # Categories Recieved
            print("Categories Recieved")
            for category in categories:
                category_model = Category(name=category, projectName=projectName)

                #create folder for assets
                create_req_folder(f"{category_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}")
                #create folder for assets thumbnails
                create_req_folder(f"{cat_thumbnail_folder.replace("Category","Asset")}/{category.replace(" ","_").lower()}")

                await collection.insert_one(category_model.model_dump())
            return {
                "message": f"{len(categories)} Categories Created"
            }

    except Exception as e:
        print(e)
        raise HTTPException (
            status_code=500,
            detail=f"Failed to add categories: {e}"
        )

#=======================================================================================

async def get_all_categories(
    projectName
):
    try:
        project_foldername = projectName.replace(" ","_").lower()
        db = get_assets_db()
        collection = db[f"{config.CATEGORIES_COLLECTION}_{project_foldername}"]
        
        condition = {"projectName": projectName}
        print(condition)
        projection = {
            "_id":1,
            "name": 1,
            "is_premium": 1
        }
        # 1. Fetch the data
        categories = await collection.find(condition,projection).to_list(length=None)
        
        # 2. Convert ObjectId to string for every document
        for category in categories:
            category["_id"] = str(category["_id"])
        return {
            "categories": categories,
            "message": f"{len(categories)} categories fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {e}"
        )

#=======================================================================================
#=======================================================================================

async def add_assets(
    projectName,
    categoryId, 
    categoryName, 
    gifFile,
    audioFile
):
    try:
        print("In Assets Function")
        assetName = gifFile.filename.split('.')[0]
        #======================================================================

        #setting up folder names
        project_foldername = projectName.replace(" ","_").lower()
        category_foldername = categoryName.replace(" ","_").lower()
        asset_foldername = assetName.replace(" ","_").lower()
        #======================================================================
        
        #Original Asset path
        complete_folderpath = f"{config.STATIC_DIR}/{project_foldername}/Original/Asset/{category_foldername}/{asset_foldername}"
        create_req_folder(complete_folderpath)
        #======================================================================

        #setting up database collection
        db = get_assets_db()
        collection = db[f"{config.ASSETS_COLLECTION}_{project_foldername}"]
        #======================================================================        

        #url variables
        image_url = None
        thumbnail_url = None
        file_url = f"{config.FILE_URL_PREFIX}/{complete_folderpath}"
        #======================================================================        

        # saving files
        await save_single_file_by_folder(complete_folderpath, gifFile)
        await save_single_file_by_folder(complete_folderpath, audioFile)

        gif_url = f"{file_url}/{gifFile.filename}"
        audio_url = f"{file_url}/{audioFile.filename}"
        

        asset_model = Asset(
            category_id = categoryId,
            projectName= projectName,
            name= assetName,
            image_url= image_url,
            thumbnail_url= thumbnail_url,
            moreFields = {
                "audioFile": audio_url,
                "gifFile": gif_url
            }
        )

        await collection.insert_one(asset_model.model_dump())

        return {
            "message": "Asset Saved"
        }
    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(
            status_code=500,
            detail= f"Failed to save asset: {e}"
        )


async def get_assets(
    category_id,
    projectName
):
    try:
        db = get_assets_db()
        project_foldername = projectName.replace(" ","_").lower()
        collection = db[f"{config.ASSETS_COLLECTION}_{project_foldername}"]

        condition = {"projectName": projectName}
        projection = {
            "_id":1,
            "name": 1,
            "is_premium": 1,
            "moreFields": 1
        }
        if category_id:
            condition["category_id"] = category_id

        print(condition)

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

async def updateAsset(frame_id, requiredFunction):
    try:
        db = get_assets_db()
        collection = db[config.ASSETS_COLLECTION]

        condition = {}
        if frame_id:
            condition["_id"] = ObjectId(frame_id)

        updateSet = {}
        message = ""
        if requiredFunction == "view":
            updateSet = {"$inc" : {"views": 1}}
            message = "View Increased"
        elif requiredFunction == "enable":
            updateSet = {"$set" : {"is_enabled": True}}
            message = "Asset Enabled"
        elif requiredFunction == "disable":
            updateSet = {"$set" : {"is_enabled": False}}
            message = "Asset Disabled"
        elif requiredFunction == "premium":
            updateSet = {"$set" : {"is_premium": True}}
            message = "Asset Made Premium"
        elif requiredFunction == "notPremium":
            updateSet = {"$set" : {"is_premium": False}}
            message = "Asset Removed Premium"
        else:
            raise ValueError("No function defined / Wrong function name")

        result = await collection.update_one(condition, updateSet)

        if result.matched_count == 0:
            return {"error": "Asset not found"}
        
        return {"message": message}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update asset view: {e}"
        )