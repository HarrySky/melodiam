from typing import Any, Dict, List, Optional, Union

from starlette import status
from starlette.responses import JSONResponse


def envelope(
    data: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
    description: Optional[str] = None,
    status: int = status.HTTP_200_OK,
) -> JSONResponse:
    return JSONResponse(
        {
            "ok": 200 <= status < 300,
            "description": description,
            "data": data,
        },
        status_code=status,
    )
