from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.client import Client
from app.schemas.catalog import ClientCreate, ClientUpdate, ClientResponse
from app.api.deps import get_current_user, require_builder

router = APIRouter(prefix="/clients", tags=["Clientes"])


@router.get("/", response_model=list[ClientResponse], dependencies=[Depends(get_current_user)])
def list_clients(db: Session = Depends(get_db)):
    return db.query(Client).order_by(Client.name).all()


@router.get("/{client_id}", response_model=ClientResponse, dependencies=[Depends(get_current_user)])
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client


@router.post("/", response_model=ClientResponse, status_code=201, dependencies=[Depends(require_builder)])
def create_client(data: ClientCreate, db: Session = Depends(get_db)):
    client = Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.patch("/{client_id}", response_model=ClientResponse, dependencies=[Depends(require_builder)])
def update_client(client_id: int, data: ClientUpdate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(client, k, v)
    db.commit()
    db.refresh(client)
    return client
