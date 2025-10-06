from fastapi import APIRouter
from .upload import router as upload_router
from .files import router as files_router

router = APIRouter()

router.include_router(upload_router, prefix="/upload", tags=["media-upload"])
router.include_router(files_router, prefix="/files", tags=["media-files"])

__all__ = ["router"]