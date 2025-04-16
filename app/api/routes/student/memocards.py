from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import List

from app.services.memocard_service import MemocardService
from app.middleware.role_checker import get_student_user
from app.schemas.memocard import MemocardResponse
from app.schemas.response import ResponseCreate, ResponseResponse
from app.core.logging_config import logger

router = APIRouter(prefix="/memocards", tags=["Student - Memocards"])

@router.get("/", response_model=List[MemocardResponse], summary="Get memocards for student")
async def get_memocards_for_student(
    skip: int = Query(0, ge=0, description="Skip N memocards"),
    limit: int = Query(100, ge=1, le=100, description="Limit to N memocards"),
    current_user = Depends(get_student_user),
    memocard_service: MemocardService = Depends()
):
    """
    Get a list of memocards for the current student
    
    - **skip**: Number of memocards to skip
    - **limit**: Maximum number of memocards to return
    
    Requires student role
    """
    try:
        student_level = current_user.get("student_profile", {}).get("level")
        if not student_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student has no level"
            )
        
        return await memocard_service.get_memocards_for_student(
            str(current_user["_id"]),
            student_level,
            skip,
            limit
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
    current_user = Depends(get_student_user),
    memocard_service: MemocardService = Depends()
):
    """
    Get a memocard by ID
    
    - **memocard_id**: ID of the memocard to retrieve
    
    Requires student role
    """
    try:
        return await memocard_service.get_memocard(memocard_id)
    except Exception as e:
        logger.error(f"Memocard retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{memocard_id}/respond", response_model=ResponseResponse, summary="Respond to a memocard")
async def respond_to_memocard(
    response_data: ResponseCreate,
    memocard_id: str = Path(..., description="Memocard ID"),
    current_user = Depends(get_student_user),
    memocard_service: MemocardService = Depends()
):
    """
    Submit a response to a memocard
    
    - **memocard_id**: ID of the memocard to respond to
    - **answer**: The student's answer
    - **time_spent_seconds**: Time spent in seconds (optional)
    
    Requires student role
    """
    try:
        # Verify memocard_id matches the one in the path
        if response_data.memocard_id != memocard_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Memocard ID in path does not match the one in request body"
            )
        
        return await memocard_service.verify_answer(
            memocard_id,
            str(current_user["_id"]),
            response_data.answer,
            response_data.time_spent_seconds
        )
    except Exception as e:
        logger.error(f"Memocard response failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 