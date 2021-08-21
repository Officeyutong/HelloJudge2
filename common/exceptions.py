from typing import Any, List, Optional, Text, Tuple
from werkzeug.exceptions import HTTPException
from common.utils import make_json_response


class APIException(HTTPException):
    code = -1
    message = "Error"
    def __init__(self, message: str = None, code: int = 0) -> None:
        if message is None:
            self.message = type(self).message
        else:
            self.message = message
        self.code = code
        super().__init__(description=self.message, response=None)

    def get_body(self, environ: Optional[Any]) -> Text:
        return make_json_response(code=self.code, message=self.message)

    def get_headers(self, environ: Optional[Any]) -> List[Tuple[str, str]]:
        return [('Content-Type', 'application/json')]
