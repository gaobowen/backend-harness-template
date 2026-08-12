from pydantic import BaseModel


class ApiResponse[T](BaseModel):
    code: int = 200
    data: T
    msg: str = ""


def ok[T](data: T) -> ApiResponse[T]:
    return ApiResponse(data=data)


def fail(*, code: int, msg: str, error_code: str) -> ApiResponse[dict[str, str]]:
    return ApiResponse(code=code, data={"error_code": error_code}, msg=msg)
