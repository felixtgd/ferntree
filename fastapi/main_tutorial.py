from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from typing import Annotated, Any
from datetime import datetime, time, timedelta
from uuid import UUID

from fastapi import FastAPI, Query, Path, Body


class Image(BaseModel):
    url: str
    name: str


# Use Field to add metadata to the request body parameters
# Use nested models
class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class RoofTilt(int, Enum):
    flat = 0
    tilted30 = 30
    tilted45 = 45


class RoofAzimuth(int, Enum):
    south = 0
    south_east = -45
    south_west = 45
    east = -90
    west = 90
    north_east = -135
    north_west = 135
    north = 180


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


# Use Annotated to add metadata to the query parameter
@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")
    ] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# # Response Model - Return type
# @app.post("/items/")
# async def create_item(item: Item) -> Item:
#     return item


# @app.get("/items/")
# async def read_items() -> list[Item]:
#     return [
#         Item(name="Portal Gun", price=42.0),
#         Item(name="Plumbus", price=32.0),
#     ]


# Or use responce_model instead of return type:
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user


# Number validations: gt (greater than), lt (less than), ge (greater than or equal), le (less than or equal)
@app.get("/items/{item_id}")
async def read_item(
    *,
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str,
    size: Annotated[float, Query(gt=0, lt=10.5)],
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# item_id: path parameter
# item: request body (because Pydantic model)
# q: query parameter (because singular type)
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


@app.put("/items/{item_id}")
async def put_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
