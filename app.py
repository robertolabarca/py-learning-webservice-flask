from fastapi import FastAPI
from enum import Enum

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

class ModelName(str, Enum): 
    alexnet="alexnet"
    resnet="resnet"
    lenet="lenet"

app=FastAPI()

@app.get("/")
async def root():
    """
    docstring
    """
    return {"message":"Hello"}

@app.get("/iitems/{item_id}")
async def read_iitem(item_id:int):
    """
    docstring
    """
    return {"item_id":item_id}

@app.get("/models/{model_name}")
async def read_model(model_name:ModelName):
    """
    docstring
    """
    result=None

    if model_name is ModelName.alexnet:
        result = {
            'model_name': model_name,
            'message': 'Deep Learning FTW!'
        }
    if model_name.value == "lenet":
        result = {
            'model_name': model_name,
            'message': 'LeCNN all the images'
        }
    else:
        result = {
            'model_name': model_name,
            'message': 'Have some residuals'
        }
    
    return result

@app.get("/fakedb/items/")
async def read_item(skip:int=0,limit:int=10):
    return fake_items_db[skip:skip+limit]

@app.get("/fakedb/items/{item_id}")
async def read_item_one(item_id:int, q:str | None=None):
    if q:
        return {"item_id":item_id, "q":q}
    return  {"item_id":item_id}

@app.get("/fakedb/items/dos/{item_id}")
async def read_item_dos(item_id:int, q:str | None=None,search_in_fake_db:bool=False):
    result = {"id":item_id}
    if q:
        result.update({"q":q})
    
    if search_in_fake_db:
        result.update ({"search_in_db":"Buscar en BD"})
        result.update(get_itemvalue_fake_db(item=item_id))  

    return result

def get_itemvalue_fake_db(item:int):
    """
    docstring
    """
    result={"Error":"Index fuera de rango"}

    if 0 <= item < len(fake_items_db):
        result={"item_name":fake_items_db[item]}
    
    return result
