from typing import Annotated

from fastapi import Depends, Request
from gensim.models import KeyedVectors


def get_model(request: Request):
    return request.app.state.model


ModelDep = Annotated[KeyedVectors, Depends(get_model)]
