
from fastapi import FastAPI

app = FastAPI()

# hello world
@app.get("/") # get request 
async def root():
    return {"message": "hello world"}



# item id example
# item id has to be an int
"""
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
"""



# user id example
# /users/me leads to user's own profile
# anything other than /users/me leads to other profiles
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"} 
    # this path operation will beat out the 
    # second since it's defined first

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}



from enum import Enum

# almost same as above but with enums
class ModelName(str, Enum):
    alexnet = "coldmuffin"
    resnet = "tislam"
    lenet = "ramen"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "level 500 ceo"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "ts level 500 ceo"}

    return {"model_name": model_name, "message": "level 500 ramen ceo"}



# reads file path
@app.get("/files/{file_path:path}") # without ":path", /file/1/2 would return an error
async def read_file(file_path: str):
    return {"file_path": file_path}



# query parameters
# http://127.0.0.1:8000/items/ default parameters
# http://127.0.0.1:8000/items/?begin=1&limit=3 begin = 1, limit = 3
items_db = []
for i in range(1, 6):
    items_db.append({"item_name": f"Item {i}"})

@app.get("/items/")
async def read_item(begin: int = 0, limit: int = 3): # if not specified in the url, default to this
    return items_db[begin : begin + limit]



# boolean query parameters
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item



from fastapi.params import Body

# post request
# this function expects the client to send a json in this structure
# {
#   "title": ...
#   "content": ...
# }
# and the api server returns whatever the return statement in the function sends
@app.post('/create/post')
async def create_post(payload: dict = Body(...)): # (...) = (required = True)
    print(payload)
    return {
        "message" : "Successfuly created post!", 
        "new_post": f"title: {payload['title']} content: {payload['content']}"
    }



from pydantic import BaseModel
from typing import Optional

# same post request but with a pydantic model
class Card(BaseModel):
    title: str
    description: Optional[str] = None # optional field
    field: str
    cost: int = -1 # defaults to None if no cost is provided

@app.post('/create/card')
async def create_card(new_card: Card):
    print(dict(new_card))
    return {
        "title": new_card.title,
        "description": new_card.description,
        "field": new_card.field,
        "cost": new_card.cost
    }
