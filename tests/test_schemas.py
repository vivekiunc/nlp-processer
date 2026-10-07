import pytest
from pydantic import ValidationError

from app.schemas import QueryRequest, RetrievedChunk, RetrieveResponse


def test_query_request_defaults_top_k_to_three():
    request = QueryRequest(query="hello")
    assert request.top_k == 3


def test_query_request_rejects_empty_query():
    with pytest.raises(ValidationError):
        QueryRequest(query="")


@pytest.mark.parametrize("top_k", [0, -1, 11, 100])
def test_query_request_rejects_out_of_range_top_k(top_k):
    with pytest.raises(ValidationError):
        QueryRequest(query="hello", top_k=top_k)


@pytest.mark.parametrize("top_k", [1, 10])
def test_query_request_accepts_boundary_top_k(top_k):
    request = QueryRequest(query="hello", top_k=top_k)
    assert request.top_k == top_k


def test_retrieved_chunk_allows_missing_optional_fields():
    chunk = RetrievedChunk(text="some text")
    assert chunk.source is None
    assert chunk.crop is None


def test_retrieve_response_wraps_chunk_list():
    response = RetrieveResponse(chunks=[{"text": "t", "source": "s.pdf"}])
    assert len(response.chunks) == 1
    assert response.chunks[0].source == "s.pdf"
