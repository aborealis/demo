from typing import NoReturn
import uuid
from copy import deepcopy
from typing import Dict, Any, Union
from fastapi import HTTPException


OpenAPIResponsesDict = Dict[int | str, Dict[str, Any]]


class DictMerger:
    """Helper to merge OpenAPI response mappings."""

    def __init__(self) -> None:
        self.counter = 0

    def merge_responses(self, *responses: OpenAPIResponsesDict) -> OpenAPIResponsesDict:
        """
        Execute merge responses.
        """
        result: OpenAPIResponsesDict = {}
        counter = self.counter

        for resp in responses:
            for status_code, content in resp.items():
                app_json = content["content"]["application/json"]

                if status_code not in result:
                    result[status_code] = deepcopy(content)
                    continue

                result_app_json = result[status_code]["content"]["application/json"]

                if "example" in result_app_json:
                    description = result[status_code]["description"]
                    counter = 1
                    key = f"{counter}: {description}"
                    existing = result_app_json.pop("example")
                    result_app_json["examples"] = {key: {"value": existing}}

                if "example" in app_json:
                    description = resp[status_code]["description"]
                    counter += 1
                    key = f"{counter}: {description}"
                    result_app_json["examples"][key] = {
                        "value": app_json["example"]}
                elif "examples" in app_json:
                    result_app_json["examples"].update(
                        deepcopy(app_json["examples"]))

        return result


dict_merger = DictMerger()


class OpenAPIResponses:
    """OpenAPI response schema container."""

    def __init__(self, responses: OpenAPIResponsesDict):
        self.responses = responses

    def __add__(self, other: Union["ApiError", "MessageResponse"]):
        if hasattr(other, "openapi"):
            return OpenAPIResponses(
                dict_merger.merge_responses(self.responses, other.openapi)
            )
        return NotImplemented

    @property
    def openapi(self) -> OpenAPIResponsesDict:
        return self.responses


class ApiError:
    """Standard API error response schema."""

    def __init__(self,
                 status_code: int,
                 description: str,
                 detail: str,
                 code: str | None = None,
                 headers: dict[str, Any] | None = None,
                 ):
        self._status_code = status_code
        self._description = description
        self._detail = detail
        self._code = code or str(uuid.uuid4())
        self._headers = headers

    def raise_exception(self, err_message: str | None = None) -> NoReturn:
        exception = HTTPException(
            status_code=self._status_code,
            detail=err_message or self._detail,
        )
        if self._headers:
            exception.headers = self._headers
        raise exception

    @property
    def openapi(self) -> OpenAPIResponsesDict:
        return {
            self._status_code: {
                "description": self._description,
                "content": {
                    "application/json": {
                        "example": {
                            "detail": self._detail
                        }
                    }
                },
            }
        }

    def __add__(self, other: Union["ApiError", "MessageResponse", "OpenAPIResponses"]):
        if hasattr(other, "openapi"):
            return OpenAPIResponses(
                dict_merger.merge_responses(self.openapi, other.openapi)
            )
        return NotImplemented


class MessageResponse:
    """Standard success message response schema."""

    def __init__(self, message: str, code: str | None = None,):
        self._message = message
        self._code = code or str(uuid.uuid4())

    @property
    def response(self) -> dict:
        return {"message": self._message}

    @property
    def openapi(self) -> OpenAPIResponsesDict:
        """
        Constructor for an OpenAPI response with a message.
        Used to set examples for successful operations in
        API documentation.
        """
        return {
            200: {
                "description": "Successful Response",
                "content": {
                    "application/json": {
                        "example": {"message": self._message}
                    }
                },
            }
        }

    def __add__(self, other: Union["ApiError", "MessageResponse", "OpenAPIResponses"]):
        if hasattr(other, "openapi"):
            return OpenAPIResponses(
                dict_merger.merge_responses(self.openapi, other.openapi)
            )
        return NotImplemented


if __name__ == "__main__":
    from pprint import pprint

    ERR_400_BOT_NOT_FOUND = ApiError(
        status_code=404,
        description="Not Found Dept",
        detail="Agent with the specified ID not found",
    )

    ERR_400_USER_NOT_FOUND = ApiError(
        status_code=404,
        description="Not Found User",
        detail="User with the specified ID not found",
    )

    OK_200_MESSAGE_USER_DELETED = MessageResponse("User deleted")

    result = (ERR_400_BOT_NOT_FOUND + ERR_400_USER_NOT_FOUND +
              OK_200_MESSAGE_USER_DELETED).openapi

    pprint(ERR_400_USER_NOT_FOUND.openapi)
    print(f"{'='*20} Router Decorator Response Block 2 {'='*20}")
    pprint(ERR_400_BOT_NOT_FOUND.openapi)
    print(f"{'='*20} Router Decorator Response Block 3 {'='*20}")
    pprint(OK_200_MESSAGE_USER_DELETED.openapi)
    print(f"{'='*20} Router Decorator Responce Block 4 {'='*20}")
    pprint(result)
    print(f"{'='*20} Router Decorator Responce Block 4 {'='*20}")
    pprint(result)
    print(f"{'='*20} Http return message {'='*20}")
    pprint(OK_200_MESSAGE_USER_DELETED.response)
    print(f"{'='*20} Exception raised message {'='*20}")
    try:
        ERR_400_USER_NOT_FOUND.raise_exception()
    except HTTPException as e:
        print(e)
