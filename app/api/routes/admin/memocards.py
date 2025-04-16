from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List, Optional, Dict, Any

from app.services.memocard_service import MemocardService
from app.middleware.role_checker import get_admin_user
from app.schemas.memocard import MemocardCreate, MemocardUpdate, MemocardResponse
from app.core.logging_config import logger
from app.core.config import settings

router = APIRouter(prefix="/memocards", tags=["Admin - Memocards"])

@router.post("/", response_model=MemocardResponse, summary="Create a new memocard")
async def create_memocard(
    memocard_data: MemocardCreate,
    current_user = Depends(get_admin_user),
    memocard_service: MemocardService = Depends()
):
    """
    Create a new memocard (admin only)
    
    - **title**: Memocard title
    - **description**: Memocard description
    - **level**: School level (e.g., "3e")
    - **difficulty**: Difficulty level ("easy", "medium", "hard", "expert")
    - **subject**: Subject (e.g., "Géométrie")
    - **chapter**: Chapter (e.g., "Théorème de Pythagore")
    - **type**: Question type ("true_false", "multiple_choice", "text", "numeric")
    - **is_active**: Whether the memocard is active
    - **tags**: List of tags
    - **content**: Content specific to the question type
    
    Requires admin role
    """
    try:
        result = await memocard_service.create_memocard(memocard_data, str(current_user["_id"]))
        return result
    except Exception as e:
        logger.error(f"Memocard creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[MemocardResponse], summary="Get memocards")
async def get_memocards(
    skip: int = Query(0, ge=0, description="Skip N memocards"),
    limit: int = Query(100, ge=1, le=100, description="Limit to N memocards"),
    level: Optional[str] = Query(None, description="Filter by school level"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    chapter: Optional[str] = Query(None, description="Filter by chapter"),
    current_user = Depends(get_admin_user),
    memocard_service: MemocardService = Depends()
):
    """
    Get a list of memocards with optional filters (admin only)
    
    - **skip**: Number of memocards to skip
    - **limit**: Maximum number of memocards to return
    - **level**: Filter by school level (e.g., "3e")
    - **difficulty**: Filter by difficulty level
    - **subject**: Filter by subject
    - **chapter**: Filter by chapter
    
    Requires admin role
    """
    try:
        return await memocard_service.get_memocards(
            skip, limit, level, difficulty, subject, chapter
        )
    except Exception as e:
        logger.error(f"Memocards retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{memocard_id}", response_model=MemocardResponse, summary="Get a memocard by ID")
async def get_memocard(
    memocard_id: str = Path(..., description="Memocard ID"),
    current_user = Depends(get_admin_user),
    memocard_service: MemocardService = Depends()
):
    """
    Get a memocard by ID (admin only)
    
    - **memocard_id**: ID of the memocard to retrieve
    
    Requires admin role
    """
    try:
        return await memocard_service.get_memocard(memocard_id)
    except Exception as e:
        logger.error(f"Memocard retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{memocard_id}", response_model=MemocardResponse, summary="Update a memocard")
async def update_memocard(
    memocard_data: MemocardUpdate,
    memocard_id: str = Path(..., description="Memocard ID"),
    current_user = Depends(get_admin_user),
    memocard_service: MemocardService = Depends()
):
    """
    Update a memocard (admin only)
    
    - **memocard_id**: ID of the memocard to update
    - **memocard_data**: Updated memocard data
    
    Requires admin role
    """
    try:
        return await memocard_service.update_memocard(memocard_id, memocard_data)
    except Exception as e:
        logger.error(f"Memocard update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{memocard_id}", summary="Delete a memocard")
async def delete_memocard(
    memocard_id: str = Path(..., description="Memocard ID"),
    current_user = Depends(get_admin_user),
    memocard_service: MemocardService = Depends()
):
    """
    Delete a memocard (admin only)
    
    - **memocard_id**: ID of the memocard to delete
    
    Requires admin role
    """
    try:
        await memocard_service.delete_memocard(memocard_id)
        return {"message": "Memocard deleted successfully"}
    except Exception as e:
        logger.error(f"Memocard deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 