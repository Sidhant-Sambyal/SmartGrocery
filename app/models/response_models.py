from pydantic import BaseModel


class GroceryResponse(BaseModel):
    item: str
    tag_type: str
    color: str
    metadata: dict