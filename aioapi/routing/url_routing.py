import collections
from typing import Any, Dict, List, Sequence, Tuple, Union

__all__ = [
    "RouteError",
    "Routes",
    "RouteResolved",
]

VariablePartsType = Tuple[tuple, Tuple[str, str]]


class RouteError(Exception):
    """Base error for any exception raised"""


def depth_of(parts: Sequence[str]) -> int:
    return len(parts) - 1


def normalize_url(url: str) -> str:
    if url.startswith("/"):
        url = url[1:]

    if url.endswith("/"):
        url = url[:-1]

    return url


def _unwrap(variable_parts: VariablePartsType):
    curr_parts = variable_parts
    var_any = []
    while curr_parts:
        curr_parts, (var_type, part) = curr_parts

        if var_type == Routes._VAR_ANY_NODE:
            var_any.append(part)
            continue

        if var_type == Routes._VAR_ANY_BREAK:
            if var_any:
                yield tuple(reversed(var_any))
                var_any.clear()

            var_any.append(part)
            continue

        if var_any:
            yield tuple(reversed(var_any))
            var_any.clear()
            yield part
            continue

        yield part

    if var_any:
        yield tuple(reversed(var_any))


def make_params(
    key_parts: Sequence[str], variable_parts: VariablePartsType
) -> Dict[str, Union[str, Union[str, Tuple[str]]]]:
    return dict(zip(reversed(key_parts), _unwrap(variable_parts)))  # type: ignore


_Route = collections.namedtuple("_Route", ["key_parts", "anything"])

RouteResolved = collections.namedtuple("RouteResolved", ["params", "anything"])


class Routes:
    _VAR_NODE = ":var"
    _VAR_ANY_NODE = ":*var"
    _ROUTE_NODE = ":*route"
    _VAR_ANY_BREAK = ":*break"

    def __init__(self, max_depth: int = 40) -> None:
        self._max_depth_custom = max_depth
        self._routes = {}
        self._max_depth = 0

    def _deconstruct_url(self, url: str) -> List[str]:
        parts = url.split("/", self._max_depth + 1)
        if depth_of(parts) > self._max_depth:
            raise RouteError("No match")
        return parts

    def _match(self, parts: Sequence[str]) -> RouteResolved:
        route_match = None
        route_variable_parts = tuple()
        to_visit = [(self._routes, tuple(), 0)]

        while to_visit:
            curr, curr_variable_parts, depth = to_visit.pop()

            try:
                part = parts[depth]
            except IndexError:
                if self._ROUTE_NODE in curr:
                    route_match = curr[self._ROUTE_NODE]
                    route_variable_parts = curr_variable_parts
                    break
                else:
                    continue

            if self._VAR_ANY_NODE in curr:
                to_visit.append(
                    (
                        {self._VAR_ANY_NODE: curr[self._VAR_ANY_NODE]},
                        (curr_variable_parts, (self._VAR_ANY_NODE, part)),
                        depth + 1,  # type: ignore
                    )
                )
                to_visit.append(
                    (
                        curr[self._VAR_ANY_NODE],
                        (curr_variable_parts, (self._VAR_ANY_BREAK, part)),
                        depth + 1,  # type: ignore
                    )
                )

            if self._VAR_NODE in curr:
                to_visit.append(
                    (
                        curr[self._VAR_NODE],
                        (curr_variable_parts, (self._VAR_NODE, part)),
                        depth + 1,  # type: ignore
                    )
                )

            if part in curr:
                to_visit.append((curr[part], curr_variable_parts, depth + 1))  # type: ignore

        if not route_match:
            raise RouteError("No match")

        return RouteResolved(
            params=make_params(
                key_parts=route_match.key_parts, variable_parts=route_variable_parts  # type: ignore
            ),
            anything=route_match.anything,
        )

    def match(self, url: str) -> RouteResolved:
        url = normalize_url(url)
        parts = self._deconstruct_url(url)
        return self._match(parts)

    def add(self, url: str, anything: Any) -> None:
        url = normalize_url(url)
        parts = url.split("/")
        curr_partial_routes = self._routes
        curr_key_parts = []

        for part in parts:
            if part.startswith(":*"):
                curr_key_parts.append(part[2:])
                part = self._VAR_ANY_NODE
                self._max_depth = self._max_depth_custom

            elif part.startswith(":"):
                curr_key_parts.append(part[1:])
                part = self._VAR_NODE

            curr_partial_routes = curr_partial_routes.setdefault(part, {})

        curr_partial_routes[self._ROUTE_NODE] = _Route(
            key_parts=curr_key_parts, anything=anything
        )

        self._max_depth = max(self._max_depth, depth_of(parts))
