"""Typed boundaries for an asset release and its delivery result."""

try:
    from pydantic import BaseModel, Field, HttpUrl
except ModuleNotFoundError:  # Keep the dispatcher usable in its lightweight test setup.
    from dataclasses import dataclass, field

    HttpUrl = str

    def Field(*, default=None, default_factory=None, **kwargs):
        if default_factory is not None:
            return field(default_factory=default_factory)
        return field(default=default)

    @dataclass
    class BaseModel:
        def __init__(self, **values):
            annotations = getattr(self, "__annotations__", {})
            for name in annotations:
                if name in values:
                    value = values[name]
                else:
                    class_field = getattr(self, name, None)
                    if hasattr(class_field, "default_factory") and callable(class_field.default_factory):
                        value = class_field.default_factory()
                    elif hasattr(class_field, "default"):
                        value = class_field.default
                    elif class_field is not None:
                        value = class_field
                    else:
                        raise TypeError(f"Missing required field: {name}")
                setattr(self, name, value)


class Subscriber(BaseModel):
    subscriber_id: str
    email: str
    interests: list[str] = Field(min_length=1)
    active: bool = True


class AssetRelease(BaseModel):
    release_id: str
    title: str
    creator_notes: str
    download_url: HttpUrl
    subscribers: list[Subscriber] = Field(min_length=1)
    similarity_threshold: float = Field(default=0.75, ge=-1.0, le=1.0)

    def __init__(self, **values):
        values["subscribers"] = [
            item if isinstance(item, Subscriber) else Subscriber(**item)
            for item in values.get("subscribers", [])
        ]
        super().__init__(**values)


class DeliveryNotice(BaseModel):
    subscriber_id: str
    email: str
    subject: str
    summary: str
    download_url: HttpUrl


class DispatchResult(BaseModel):
    release_id: str
    summary: str
    notices: list[DeliveryNotice]
