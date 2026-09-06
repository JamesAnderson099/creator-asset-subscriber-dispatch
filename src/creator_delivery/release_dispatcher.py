"""Turn creator notes into targeted subscriber delivery notices."""

from math import sqrt
from typing import Any

from .request_models import AssetRelease, DeliveryNotice, DispatchResult


def _cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_size = sqrt(sum(value * value for value in left))
    right_size = sqrt(sum(value * value for value in right))
    if left_size == 0 or right_size == 0:
        return 0.0
    return numerator / (left_size * right_size)


class ReleaseDispatcher:
    def __init__(self, ai: Any) -> None:
        self.ai = ai

    def dispatch(self, release: AssetRelease) -> DispatchResult:
        completion = self.ai.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": "Write a factual subscriber update in two short sentences.",
                },
                {
                    "role": "user",
                    "content": f"Asset: {release.title}\nCreator notes: {release.creator_notes}",
                },
            ],
        )
        summary = completion.choices[0].message.content
        if not summary:
            raise ValueError("Content processing returned an empty summary")

        active = [subscriber for subscriber in release.subscribers if subscriber.active]
        if not active:
            return DispatchResult(release_id=release.release_id, summary=summary, notices=[])

        interest_text = [", ".join(subscriber.interests) for subscriber in active]
        embedded = self.ai.embeddings.create(model="auto", input=[summary, *interest_text])
        vectors = [item.embedding for item in embedded.data]
        if len(vectors) != len(active) + 1:
            raise ValueError("Embedding response did not match the requested inputs")

        notices = [
            DeliveryNotice(
                subscriber_id=subscriber.subscriber_id,
                email=subscriber.email,
                subject=f"New asset: {release.title}",
                summary=summary,
                download_url=release.download_url,
            )
            for subscriber, vector in zip(active, vectors[1:], strict=True)
            if _cosine(vectors[0], vector) >= release.similarity_threshold
        ]
        return DispatchResult(
            release_id=release.release_id,
            summary=summary,
            notices=notices,
        )
