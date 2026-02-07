from typing import Any, Callable, Dict, List, Optional, Type, Union

class FastAPI:
    def __init__(self, title: str = "FastAPI", version: str = "0.1.0"):
        self.title = title
        self.version = version
        self.router = APIRouter()

    def get(self, path: str, **kwargs):
        return self.router.get(path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.router.post(path, **kwargs)

class APIRouter:
    def __init__(self):
        self.routes = []

    def get(self, path: str, **kwargs):
        def decorator(func: Callable):
            self.routes.append({"path": path, "method": "GET", "func": func})
            return func
        return decorator

    def post(self, path: str, **kwargs):
        def decorator(func: Callable):
            self.routes.append({"path": path, "method": "POST", "func": func})
            return func
        return decorator
