from pydantic import BaseModel
from typing import List

class BdongCodeItem(BaseModel):
    code: str
    name: str

class BdongCodeResponse(BaseModel):
    message: List[BdongCodeItem]