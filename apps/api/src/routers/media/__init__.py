from fastapi import APIRouter
from . import upload, files

router = APIRouter()

__all__ = ["upload", "files", "router"]
