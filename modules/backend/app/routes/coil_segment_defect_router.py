from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.coil_segment_defect_schemas import CoilSegmentDefectSchema, CoilSegmentDefectUpdateSchema
from use_cases.coil_segment_defect_use_cases import CoilSegmentDefectUseCases
from db.database import get_db

router = APIRouter(prefix="/coil_segment_defect", tags=["CoilSegmentDefect"])


@router.post("/add", summary="Add defect to coil segment", response_description="Defect successfully added")
def add_coil_segment_defect(
    coil_segment_defect: CoilSegmentDefectSchema,
    db_session: Session = Depends(get_db)
):
    """
    Add a new defect to a specific coil segment.

    - **coil_segment_defect**: Object containing defect class ID and defect data.
    - **Returns**: Success message if added, or 404 if defect class is not found.
    """
    try:
        if not CoilSegmentDefectUseCases.check_defect_class(coil_segment_defect.defect_class_id, db_session):
            raise HTTPException(status_code=404, detail="Defect class not found")

        CoilSegmentDefectUseCases.add_coil_segment_defect(coil_segment_defect=coil_segment_defect, db_session=db_session)
        return {"message": "Coil segment defect added successfully"}
    
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding coil segment defect: {str(e)}")


@router.delete("/remove/{coil_segment_defect_id}", summary="Remove defect by ID", response_description="Defect successfully removed")
def remove_coil_segment_defect(
    coil_segment_defect_id: int,
    db_session: Session = Depends(get_db)
):
    """
    Remove a coil segment defect by its ID.

    - **coil_segment_defect_id**: ID of the defect.
    - **Returns**: Success message or 404 if not found.
    """
    try:
        success = CoilSegmentDefectUseCases.remove_coil_segment_defect_by_id(id=coil_segment_defect_id, db_session=db_session)
        if success:
            return {"message": "Coil segment defect removed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Coil segment defect not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing coil segment defect: {str(e)}")


@router.put("/update/{coil_segment_defect_id}", summary="Update defect by ID", response_description="Defect successfully updated")
def update_coil_segment_defect(
    coil_segment_defect_id: int,
    coil_segment_defect_data: CoilSegmentDefectUpdateSchema,
    db_session: Session = Depends(get_db)
):
    """
    Update the data of a specific coil segment defect.

    - **coil_segment_defect_id**: ID of the defect to update.
    - **coil_segment_defect_data**: Fields to update.
    - **Returns**: Success message or 404 if not found.
    """
    try:
        success = CoilSegmentDefectUseCases.update_coil_segment_defect_by_id(
            id=coil_segment_defect_id,
            coil_segment_defect_data=coil_segment_defect_data,
            db_session=db_session
        )
        if success:
            return {"message": "Coil segment defect updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Coil segment defect not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating coil segment defect: {str(e)}")


@router.get("/list", summary="List all coil segment defects", response_description="List of all coil segment defects")
def list_coil_segment_defects(db_session: Session = Depends(get_db)):
    """
    Retrieve all coil segment defects stored in the system.

    - **Returns**: List of all coil segment defects.
    """
    try:
        coil_segment_defects = CoilSegmentDefectUseCases.list_coil_segment_defects(db_session=db_session)
        return {"coil_segment_defects": coil_segment_defects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing coil segment defects: {str(e)}")


@router.get("/get/{coil_segment_defect_id}", summary="Get defect by ID", response_description="Details of the defect")
def get_one_coil_segment_defect(
    coil_segment_defect_id: int,
    db_session: Session = Depends(get_db)
):
    """
    Retrieve details of a single coil segment defect by its ID.

    - **coil_segment_defect_id**: ID of the defect to retrieve.
    - **Returns**: Defect details or 404 if not found.
    """
    try:
        coil_segment_defect = CoilSegmentDefectUseCases.get_coil_segment_defect_by_id(id=coil_segment_defect_id, db_session=db_session)
        if coil_segment_defect:
            return coil_segment_defect
        else:
            raise HTTPException(status_code=404, detail="Coil segment defect not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting coil segment defect: {str(e)}")


@router.get("/defects_by_fragment/{coil_segment_id}", summary="Get defects by segment ID", response_description="List of defects for the given segment")
def get_defects_by_fragment_id(
    coil_segment_id: int,
    db_session: Session = Depends(get_db)
):
    """
    Retrieve all defects associated with a specific coil segment (fragment).

    - **coil_segment_id**: ID of the coil segment.
    - **Returns**: List of defects for that fragment or 404 if none found.
    """
    try:
        defects = CoilSegmentDefectUseCases.get_defects_by_fragment_id(coil_segment_id, db_session)
        if defects:
            return defects
        else:
            raise HTTPException(status_code=404, detail="No defects found for the given fragment ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching defects: {str(e)}")
