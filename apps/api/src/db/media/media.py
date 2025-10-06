from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Index


class MediaFileBase(SQLModel):
    file_uuid: str = Field(index=True, unique=True)
    storage_backend: str
    file_path: str
    file_url: str
    content_type: str
    file_size: int
    resource_type: str = Field(index=True)
    resource_id: str = Field(index=True)


class MediaFile(MediaFileBase, table=True):
    __table_args__ = (
        Index("ix_media_files_resource", "resource_type", "resource_id"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class MediaFileCreate(MediaFileBase):
    pass


class MediaFileRead(MediaFileBase):
    id: int
    uploaded_at: datetime
