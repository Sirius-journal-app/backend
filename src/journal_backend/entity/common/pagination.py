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
        data: list[T]
) -> PaginationResponse[T]:
    return PaginationResponse(
        next_url=f"{uri_prefix}?offset={offset + 1}&{limit}",
        prev_url=f"{uri_prefix}?offset={offset - 1}&{limit}",
        data=data,
    )
