from fastapi import FastAPI, Query, Path
from typing import Annotated
from pydantic import BaseModel, Field

app = FastAPI()

# @app.get("/items/")
# async def read_items(q: Annotated[str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")]):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

@app.get("/items/{item_id}")
async def read_items(item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)]):
    return {"item_id": item_id}

class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: str = "created_at"
    tags: list[str] = []

@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

class Item(BaseModel):
    name: str
    description: str | None = Field(None, title="The description of the item", max_length=300)
    price: float = Field(..., title="Price of the item", gt=0)
    tax: float | None = None

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = Field(None, max_length=300)
    price: float | None = Field(None, gt=0)
    tax: float | None = None

@app.post("/items/", status_code=201)
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax:
        item_dict.update({"price_with_tax": item.price + item.tax})
    return item_dict

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}

@app.patch("/items/{item_id}")
async def partial_update_item(item_id: int, item: ItemUpdate):
    return {"item_id": item_id, **item.model_dump(exclude_unset=True)}

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    return None