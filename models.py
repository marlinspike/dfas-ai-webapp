from pydantic import BaseModel

class LlmResponse(BaseModel):
    state: str
    category: str
    subcategory: str
    rationale: str
    confidence: int
    is_match: bool

class Item(BaseModel):
    id: str
    state: str
    url: str
    created_at: str
    llm_response: list[LlmResponse]
