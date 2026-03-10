from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from controller import controller

router = APIRouter(prefix="/api/crud", tags=["shimeji"])

#=======================================================================================
#=======================================================================================

@router.get("/", response_model=dict)
async def read_root():
    return {
        "message": "CRUP App is running"
    }

#=======================================================================================

@router.post("/create_new_project", response_model=dict)
async def create_project(
    request: Request,
    projectName: str = Form(...),
    projectImage: UploadFile = File(None)
):
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter project name"}
        )
    
    result = await controller.create_project(projectName, projectImage)
    return result

@router.put("/edit_project", response_model=dict)
async def edit_project(
    request: Request,
    projectName: str = Form(...),
    newprojectName: str = Form(None),
    projectImage: UploadFile = File(None)
):
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter project name"}
        )
    
    result = await controller.update_project(projectName, projectImage, newprojectName)
    return result

@router.get("/get_projects", response_model=dict)
async def get_projects(
):

    result = await controller.get_projects()
    return result

@router.delete("/delete_project", response_model=dict)
async def delete_project(
    request: Request,
):
    projectName = request.query_params.get("projectName")
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter project name"}
        )

    result = await controller.remove_project(projectName)
    return result

#=======================================================================================
#=======================================================================================

@router.post("/add_categories", response_model=dict)
async def add_categories(
    request: Request,
    projectName: str = Form(...),
    categories: list[str] = Form(None),
    images: list[UploadFile] = File(None),
):
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter project name"}
        )

    # Set the state so the middleware can access it later
    request.state.project_name = projectName
    
    # 1. Normalize categories if they come in as an empty list/None
    has_categories = categories and len(categories) > 0
    
    # 2. Check if images were actually uploaded
    # We check for: list is not None, list is not empty, and filename is not empty
    has_images = images and len(images) > 0 and images[0].filename != ""

    if not has_categories and not has_images:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter at least one field: categories or images"}
        )

    result = await controller.add_categories(categories, projectName, images, has_images)
    return result

@router.get("/get_categories", response_model=dict)
async def get_categories(
    request: Request,
):
    projectName = request.query_params.get("projectName")
    isAdmin = request.query_params.get("isAdmin")
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter project name"}
        )

    # Set the state so the middleware can access it later
    request.state.project_name = projectName


    result = await controller.get_all_categories(projectName, isAdmin)
    return result

@router.put("/edit_category", response_model=dict)
async def edit_category(
    request: Request,
    projectName: str = Form(...),
    categoryId: str = Form(None),
    categoryName: str = Form(None),
    categoryImage: UploadFile = File(None),
    isEnable: bool = Form(None),
    isPremium: bool= Form(None)
):
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter project name"}
        )
    if not categoryId:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "CategoryId missing"}
        )
    
    result = await controller.update_category(projectName, categoryId, categoryName, categoryImage, isEnable, isPremium)
    return result

@router.delete("/delete_category", response_model=dict)
async def delete_category(
    request: Request,
):
    projectName = request.query_params.get("projectName")
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter project name"}
        )
    categoryId = request.query_params.get("categoryId")
    if not categoryId:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter Category ID"}
        )

    result = await controller.remove_category(projectName, categoryId)
    return result

#=======================================================================================
#=======================================================================================

@router.post("/create_asset", response_model=dict)
async def create_asset(
    request: Request,
    projectName: str = Form(...),
    categoryId: str = Form(...),
    categoryName: str = Form(...),
    name: str = Form(...),
    image: UploadFile = File(None),
    thumbnail: UploadFile = File(None),
    isEnable: bool = Form(None),
    isPremium: bool = Form(None),
    sequence: int = Form(None)
):
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter ProjectName"}
        )

    # Set the state so the middleware can access it later
    request.state.project_name = projectName
    
    if not categoryId or not categoryName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Category Params missing"}
        )
    result = await controller.add_new_asset(
        projectName,
        categoryId, 
        categoryName, 
        name, 
        image,
        thumbnail,
        isPremium,
        isEnable,
        sequence
    )

    return result

@router.get("/get_assets", response_model=dict)
async def get_assets(
    request: Request
):
    projectName = request.query_params.get("projectName")
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter project name"}
        )

    # Set the state so the middleware can access it later
    request.state.project_name = projectName
    categoryId = request.query_params.get("categoryId")
    isAdmin = request.query_params.get("isAdmin")
    
    # Get assets from database
    result = await controller.get_assets(categoryId, projectName, isAdmin)
    return result

@router.delete("/delete_asset", response_model=dict)
async def delete_asset(
    request: Request,
):
    projectName = request.query_params.get("projectName")
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter project name"}
        )
    categoryName = request.query_params.get("categoryName")
    if not categoryName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter Category Name"}
        )
    assetName = request.query_params.get("assetName")
    if not assetName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter Asset Name"}
        )
    assetId = request.query_params.get("assetId")
    if not assetId:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter Asset ID"}
        )

    result = await controller.remove_asset(
        projectName, 
        categoryName,
        assetName,
        assetId
    )
    return result

@router.put("/edit_asset", response_model= dict)
async def edit_asset(
    projectName: str = Form(...),
    categoryName: str = Form(...),
    assetName: str = Form(...),
    assetId: str = Form(...),
    assetNewName: str = Form(None),
    image: UploadFile = File(None),
    thumbnail: UploadFile = File(None),
    isEnable: str = Form(None),
    isPremium: str = Form(None),
    sequence: str = Form(None),
    views: str = Form(None)
):
    if assetNewName is None and image is None and thumbnail is None and isEnable is None and isPremium is None and sequence is None and views is None:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "No Value available for updating"}
        )

    result = await controller.update_asset(
        projectName, categoryName, assetName, assetId,
        assetNewName, image, thumbnail,
        isEnable, isPremium, sequence, views
    )

    return result

@router.patch("/incrementView", response_model=dict)
async def incrementViews(
    request: Request
):
    projectName = request.query_params.get("projectName")
    if not projectName:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Missing Project Name"}
        )
    assetId = request.query_params.get("assetId")
    if not assetId:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Missing Asset ID"}
        )

    result = await controller.increaseView(projectName, assetId)

    return result

#=======================================================================================
#=======================================================================================


@router.put("/addMoreFields", response_model=dict)
async def addingFields(
    request: Request,
    projectName: str = Form(...),
    categoryName: str = Form(...),
    assetName: str = Form(...),
    assetId: str = Form(None)
):
    result = await controller.addMoreFields(
        request,
        projectName,
        categoryName,
        assetId,
        assetName
    )
    return result

@router.delete("/deleteMoreFields", response_model=dict)
async def deletingFields(
    projectName: str = Form(...),
    assetId: str = Form(None),
    fields_to_delete: list[str] = Form(...)
):
    result = await controller.deleteMoreFields(
        projectName,
        assetId,
        fields_to_delete
    )
    return result