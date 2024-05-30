from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PaginationResponse(Generic[T]):
    next_url: str
    prev_url: str
    data: list[T]


def generate_pagination_response(
        uri_prefix: str,
        offset: int,
        limit: int,
        max_offset: int,
        data: list[T]
) -> PaginationResponse[T]:
    prev_url = f"{uri_prefix}?offset={offset - limit}&{limit=}"
    if offset - limit < 0:
        prev_url = ""

    next_url = f"{uri_prefix}?offset={offset + limit}&{limit=}"
    if offset + limit >= max_offset:
        next_url = ""

    return PaginationResponse(
        next_url=next_url,
        prev_url=prev_url,
        data=data,
    )
