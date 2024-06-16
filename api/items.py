from fastapi import APIRouter
from mock_datas.fackdb import fake_db

from schemas import items as ItemSchema

router = APIRouter(
    tags=["items"],
    prefix="/api"
)

@router.get("/items/{item_id}", response_model=ItemSchema.ItemRead)
def get_items_without_typing(item_id, qry):
    if item_id not in fake_db["items"]:
        return {"error": "Item not found"}
    return {"item": fake_db["items"][item_id], "query": qry}


@router.post("/items", response_model=ItemSchema.ItemCreate)
def create_items(item: ItemSchema.ItemCreate):
    fake_db["items"][item.id] = item
    return item


@router.delete("/items/{item_id}")
def delete_items(item_id: int):
    item = fake_db["items"].pop(item_id)
    return item