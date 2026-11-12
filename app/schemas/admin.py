from typing import Literal

from pydantic import BaseModel


class UserRoleUpdate(BaseModel):
    role: Literal["employee", "hr", "admin"]


class UserStatusUpdate(BaseModel):
    is_active: bool


class DocumentPermissionUpdate(BaseModel):
    permission: Literal["read"]
