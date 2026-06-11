from pydantic import BaseModel


class GroceryRequest(BaseModel):
    item: str


class LoginRequest(BaseModel):
    email: str