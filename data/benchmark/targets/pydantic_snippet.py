from typing import Any, Dict, Optional, Type, Union

class BaseModel:
    def __init__(self, **data: Any):
        self.__dict__.update(data)
        self.validate(data)

    @classmethod
    def validate(cls, value: Any) -> "BaseModel":
        # Simplified validation logic
        return value

    def json(self) -> str:
        import json
        return json.dumps(self.__dict__)

def Field(default: Any = ..., **kwargs: Any) -> Any:
    return default
