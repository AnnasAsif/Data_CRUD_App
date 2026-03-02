from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi import HTTPException

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

#=======================================================================================
#=======================================================================================

@router.post("/add_assets", response_model=dict)
async def add_assets(
    request: Request,
    projectName: str = Form(...),
    categoryId: str = Form(...),
    categoryName: str = Form(...),
    gifFile: UploadFile = File(...),
    audioFile: UploadFile = File(...)
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
    if not gifFile or not audioFile:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Missing Files"}
        )
    result = await controller.add_assets(
        projectName,
        categoryId, 
        categoryName, 
        gifFile, 
        audioFile)

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
    category_id = request.query_params.get("category_id")
    
    # Get assets from database
    result = await controller.get_assets(category_id, projectName)
    return result

#=======================================================================================
#=======================================================================================

@router.put("/updateAsset", response_model=dict)
async def updateAsset(
    request: Request
):
    frame_id = request.query_params.get("frame_id")
    requiredFunction = request.query_params.get("requiredFunction")

    if not frame_id:
        raise HTTPException(
            status_code=400,
            detail="Frame ID is missing"
        )
    if not requiredFunction:
        raise HTTPException(
            status_code=400,
            detail="requiredFunction is missing"
        )

    result = await controller.updateAsset(frame_id, requiredFunction)
    return result

#=======================================================================================
#=======================================================================================