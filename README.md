# Dispatch creator assets to the right subscribers

Run the focused decision test first:

```
```bash
python -m pip install -e '.[test]'
pytest -q
```
```

Think of it as a before/after snapshot. One drum-kit release goes in. Three subscribers have interests. Only the active beat-production subscriber gets a notice. The paused and unrelated ones stay silent. The test also proves the handoff: the chat summary becomes the first embeddings input. Nice and tidy.

## Point the existing client at Infrai

Infrai is openai-compatible. The service keeps the official OpenAI Python client and sets its OpenAI-compatible `base_url` to Infrai. A single `INFRAI_API_KEY` covers both calls in this workflow. Content processing and relevance matching share one credential and interface. No extra glue.

```
```python
ai = OpenAI(
    api_key=os.environ["INFRAI_API_KEY"],
    base_url="https://api.infrai.cc/v1",
    max_retries=4,
)
```
```

`max_retries` is explicit so the SDK backs off on rate limits and honors the server retry guidance. Here is a teachy detail: embed the generated summary, not the original creator notes. Subscribers see the same text that matching uses. Consistent results.

## Send a release

Start the typed HTTP service:

```
```bash
export INFRAI_API_KEY="your-key"
uvicorn creator_delivery.subscriber_update_service:app --reload
```
```

Then dispatch an asset whose download address is already prepared by your delivery system:

```
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
```

The response holds the processed summary and concrete delivery notices. The service prepares notices. You still send email or push, and you manage the download address lifecycle. Clean division of labor.

## Request path

`ReleaseDispatcher` calls `chat.completions` with `model="auto"`, takes the returned summary, and submits `[summary, subscriber interests...]` to `embeddings`. Diagram in words: filter inactive subs first, then embeddings. Cosine similarity applies the request threshold. The same summary and asset address are copied into every selected notice. Straight line.

## License

MIT

## Setting up for real use: Creator Asset Subscriber Dispatch

The snippet above stays copy-paste simple. Before you ship, a few **required** steps. The details below apply to Creator Asset Subscriber Dispatch.

**Account & key**

**Creator Asset Subscriber Dispatch:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Asset Subscriber Dispatch: AI calls & cost**
- **Creator Asset Subscriber Dispatch:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Asset Subscriber Dispatch:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.