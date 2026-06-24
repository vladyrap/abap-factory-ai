from typing import Optional
from pydantic import BaseModel


class ClientBase(BaseModel):
    name: str
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    naming_convention: Optional[str] = None
    coding_standards: Optional[str] = None
    restrictions: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    naming_convention: Optional[str] = None
    coding_standards: Optional[str] = None
    restrictions: Optional[str] = None
    notes: Optional[str] = None


class ClientResponse(ClientBase):
    id: int

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    sap_version: str = "S4HANA"
    modules: list[str] = []
    sap_package: Optional[str] = None
    transport_request: Optional[str] = None
    mandante: Optional[str] = None
    environment: str = "DEV"


class ProjectCreate(ProjectBase):
    client_id: int


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    sap_version: Optional[str] = None
    modules: Optional[list[str]] = None
    sap_package: Optional[str] = None
    transport_request: Optional[str] = None
    mandante: Optional[str] = None
    environment: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    client_id: int
    owner_user_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True
