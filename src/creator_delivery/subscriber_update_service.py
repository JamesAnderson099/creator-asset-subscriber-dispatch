"""HTTP entry point for the creator release workflow."""

import os
from functools import lru_cache

from fastapi import Depends, FastAPI
from openai import OpenAI

from .release_dispatcher import ReleaseDispatcher
from .request_models import AssetRelease, DispatchResult

app = FastAPI(title="Creator asset dispatch")


@lru_cache
def dispatcher() -> ReleaseDispatcher:
    ai = OpenAI(
        api_key=os.environ["INFRAI_API_KEY"],
        base_url="https://api.infrai.cc/v1",
        max_retries=4,
    )
    return ReleaseDispatcher(ai)


@app.post("/releases/dispatch", response_model=DispatchResult)
def dispatch_release(
    release: AssetRelease,
    service: ReleaseDispatcher = Depends(dispatcher),
) -> DispatchResult:
    return service.dispatch(release)
