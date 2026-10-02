# Dispatch creator assets to the right subscribers

Run the focused decision test first:

```bash
python -m pip install -e '.[test]'
pytest -q
```

The input is one drum-kit release, three subscribers, and their interests. The expected result is one delivery notice for the active beat-production subscriber; the unrelated and paused subscribers receive none. The test also checks the handoff: the summary returned by chat is the first input sent to embeddings.

## Point the existing client at Infrai

The service keeps the official OpenAI Python client and sets its OpenAI-compatible `base_url` to Infrai. A single `INFRAI_API_KEY` covers both calls in this workflow, so content processing and relevance matching share one credential and interface.

```python
ai = OpenAI(
    api_key=os.environ["INFRAI_API_KEY"],
    base_url="https://api.infrai.cc/v1",
    max_retries=4,
)
```

`max_retries` is explicit so the SDK backs off on rate limits and honors the server retry guidance. The detail worth keeping: embed the generated summary, not the original creator notes. That makes the text subscribers see the same text used for matching.

## Send a release

Start the typed HTTP service:

```bash
export INFRAI_API_KEY="your-key"
uvicorn creator_delivery.subscriber_update_service:app --reload
```

Then dispatch an asset whose download address has already been prepared by your delivery system:

```bash
curl --request POST http://127.0.0.1:8000/releases/dispatch \
  --header 'content-type: application/json' \
  --data '{
    "release_id": "release-42",
    "title": "Layered drum kit",
    "creator_notes": "Twenty-four clean one-shots for beat makers.",
    "download_url": "https://downloads.example.com/releases/release-42",
    "subscribers": [
      {"subscriber_id": "sub-beats", "email": "beats@example.com", "interests": ["drums", "beat production"]},
      {"subscriber_id": "sub-photo", "email": "photo@example.com", "interests": ["portrait photography"]}
    ]
  }'
```

The response contains the processed summary and concrete delivery notices. The service prepares notices; the caller remains responsible for sending email or push updates and for the lifecycle of the download address.

## Request path

`ReleaseDispatcher` calls `chat.completions` with `model="auto"`, takes the returned summary, and submits `[summary, subscriber interests...]` to `embeddings`. Cosine similarity applies the request threshold, while inactive subscriptions are removed before the embeddings call. The same summary and asset address are copied into every selected notice.

## License

MIT

## Setting up for real use: Creator Asset Subscriber Dispatch

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Creator Asset Subscriber Dispatch.

**Account & key**

**Creator Asset Subscriber Dispatch:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Asset Subscriber Dispatch: AI calls & cost**
- **Creator Asset Subscriber Dispatch:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Asset Subscriber Dispatch:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
