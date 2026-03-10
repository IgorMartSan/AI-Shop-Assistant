from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.defect_class_segmentation_schemas import DefectClassSegmentationSchema, DefectClassSegmentationUpdateSchema
from use_cases.defect_class_segmentation_use_cases import DefectClassSegmentationUseCases
from db.database import get_db

router = APIRouter(prefix="/defect_Segmentation_class", tags=["DefectSegmentationClass"])

@router.post(
    "/add",
    response_model=DefectClassSegmentationSchema,
    summary="Create segmentation defect class",
    description="Create a new segmentation defect class.",
    response_description="Segmentation defect class created.",
)
def add_defect_class(defect_class: DefectClassSegmentationSchema, db_session: Session = Depends(get_db)):
    """
    Endpoint para adicionar uma nova classe de defeito.
    """
    try:
        new_defect_class = DefectClassSegmentationUseCases.add(defect_class=defect_class, db_session=db_session)
        return new_defect_class
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar a classe de defeito: {str(e)}")

@router.delete(
    "/remove/{defect_class_id}",
    summary="Delete segmentation defect class",
    description="Delete a segmentation defect class by ID.",
    response_description="Segmentation defect class deleted.",
)
def remove_defect_class(defect_class_id: int, db_session: Session = Depends(get_db)):
    """
    Endpoint para remover uma classe de defeito pelo ID.
    """
    try:
        success = DefectClassSegmentationUseCases.remove_by_id(id=defect_class_id, db_session=db_session)
        if success:
            return {"message": "Classe de defeito removida com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Classe de defeito não encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover a classe de defeito: {str(e)}")

@router.put(
    "/update/{defect_class_id}",
    response_model=DefectClassSegmentationSchema,
    summary="Update segmentation defect class",
    description="Update a segmentation defect class by ID.",
    response_description="Segmentation defect class updated.",
)
def update_defect_class(defect_class_id: int, defect_class_data: DefectClassSegmentationSchema, db_session: Session = Depends(get_db)):
    """
    Endpoint para atualizar uma classe de defeito pelo ID.
    """
    try:
        updated_defect_class = DefectClassSegmentationUseCases.update_by_id(
            id=defect_class_id, 
            defect_class_data=defect_class_data, 
            db_session=db_session
        )
        if updated_defect_class:
            return updated_defect_class
        else:
            raise HTTPException(status_code=404, detail="Classe de defeito não encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar a classe de defeito: {str(e)}")

@router.get(
    "/list",
    response_model=list[DefectClassSegmentationSchema],
    summary="List segmentation defect classes",
    description="List all segmentation defect classes.",
    response_description="List of segmentation defect classes.",
)
def list_defect_classes(db_session: Session = Depends(get_db)):
    """
    Endpoint para listar todas as classes de defeitos.
    """
    try:
        defect_classes = DefectClassSegmentationUseCases.list(db_session=db_session)
        return defect_classes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar as classes de defeitos: {str(e)}")

@router.get(
    "/get/{defect_class_id}",
    response_model=DefectClassSegmentationSchema,
    summary="Get segmentation defect class",
    description="Get a segmentation defect class by ID.",
    response_description="Segmentation defect class details.",
)
def get_defect_class(defect_class_id: int, db_session: Session = Depends(get_db)):
    """
    Endpoint para obter uma classe de defeito pelo ID.
    """
    try:
        defect_class = DefectClassSegmentationUseCases.get_by_id(id=defect_class_id, db_session=db_session)
        if defect_class:
            return defect_class
        else:
            raise HTTPException(status_code=404, detail="Classe de defeito não encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter a classe de defeito: {str(e)}")
