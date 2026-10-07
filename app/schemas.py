from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(3, ge=1, le=10)


class QueryResponse(BaseModel):
    answer: str


class RetrievedChunk(BaseModel):
    text: str
    crop: str | None = None
    region: str | None = None
    language: str | None = None
    source: str | None = None
    topic: str | None = None


class RetrieveResponse(BaseModel):
    chunks: list[RetrievedChunk]


class AudioQueryResponse(BaseModel):
    transcription: str
    answer: str
