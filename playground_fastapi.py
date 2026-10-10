from fastapi import FastAPI, HTTPException

app = FastAPI()

items = ["apple", "banana"]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/items")
def create_items(item: str):
    items.append(item)
    return items


@app.get("/items/")
def list_items(limit: int = 10):
    return items[0: limit]

@app.get("/items/{item_id}")
def get_items(item_id: int):
    if item_id < len(items):
        item = items[item_id]
        return item
    else:
        raise HTTPException(status_code=404, detail="Item not found")