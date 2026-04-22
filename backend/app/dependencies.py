from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from gensim.models import KeyedVectors

from .config import Settings


def get_model(request: Request):
    return request.app.state.model


ModelDep = Annotated[KeyedVectors, Depends(get_model)]


@lru_cache
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
