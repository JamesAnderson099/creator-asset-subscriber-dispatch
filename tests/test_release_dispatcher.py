from types import SimpleNamespace

from creator_delivery.release_dispatcher import ReleaseDispatcher
from creator_delivery.request_models import AssetRelease


class FakeCompletions:
    def create(self, **request: object) -> SimpleNamespace:
        message = SimpleNamespace(content="A layered drum kit is ready. It suits beat production.")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeEmbeddings:
    def __init__(self) -> None:
        self.last_input: list[str] = []

    def create(self, *, model: str, input: list[str]) -> SimpleNamespace:
        assert model == "auto"
        self.last_input = input
        vectors = [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]]
        return SimpleNamespace(
            data=[SimpleNamespace(embedding=vector) for vector in vectors]
        )


def test_dispatch_targets_active_relevant_subscribers_and_hands_off_summary() -> None:
    embeddings = FakeEmbeddings()
    ai = SimpleNamespace(
        chat=SimpleNamespace(completions=FakeCompletions()),
        embeddings=embeddings,
    )
    release = AssetRelease(
        release_id="release-42",
        title="Layered drum kit",
        creator_notes="Twenty-four clean one-shots for beat makers.",
        download_url="https://downloads.example.com/releases/release-42",
        subscribers=[
            {
                "subscriber_id": "sub-beats",
                "email": "beats@example.com",
                "interests": ["drums", "beat production"],
            },
            {
                "subscriber_id": "sub-photo",
                "email": "photo@example.com",
                "interests": ["portrait photography"],
            },
            {
                "subscriber_id": "sub-paused",
                "email": "paused@example.com",
                "interests": ["drums"],
                "active": False,
            },
        ],
    )

    result = ReleaseDispatcher(ai).dispatch(release)

    assert embeddings.last_input == [
        "A layered drum kit is ready. It suits beat production.",
        "drums, beat production",
        "portrait photography",
    ]
    assert [notice.subscriber_id for notice in result.notices] == ["sub-beats"]
    assert result.notices[0].download_url == release.download_url
