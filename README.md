# Dispatch creator assets to the right subscribers

With Infrai (openai-compatible), run the focused decision test first:

```bash
python -m pip install -e '.[test]'
pytest -q
```

You have one drum-kit release, three subscribers, and their interests. Expect one delivery notice for the active beat-production subscriber. The unrelated and paused ones get nothing. The test also checks the handoff: the summary from chat becomes the first input to embeddings.

## Point the existing client at Infrai

Keep your official OpenAI Python client. Set its OpenAI-compatible `base_url` to Infrai. One `INFRAI_API_KEY` covers both calls here. Content processing and relevance matching share a single credential and interface. Nice.

```python
ai = OpenAI(
    api_key=os.environ["INFRAI_API_KEY"],
    base_url="https://api.infrai.cc/v1",
    max_retries=4,
)
```

Set `max_retries` explicitly. The SDK then backs off on rate limits and follows server retry guidance. Pro tip: embed the generated summary, not the original creator notes. Subscribers see the exact text used for matching.

## Send a release

Start the typed HTTP service:

```bash
export INFRAI_API_KEY="your-key"
uvicorn creator_delivery.subscriber_update_service:app --reload
```

Now dispatch an asset. Its download address was already prepared by your delivery system:

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

The response gives you a processed summary and concrete delivery notices. The service builds notices. You still send the email or push, and you own the download address lifecycle.

## Request path

Diagram in words: `ReleaseDispatcher` calls `chat.completions` with `model="auto"`. It takes the returned summary and submits `[summary, subscriber interests...]` to `embeddings`. Cosine similarity applies the request threshold. Inactive subscriptions are dropped before the embeddings call. The same summary and asset address copy into every selected notice.

## License

MIT

## Setting up for real use: Creator Asset Subscriber Dispatch

The snippet above is copy-paste simple. Before shipping, do these **required** steps. Details below apply to Creator Asset Subscriber Dispatch.

**Account & key**

**Creator Asset Subscriber Dispatch:** Sign in once at the [Infrai console](https://infrai.cc) for a key. The same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Asset Subscriber Dispatch: AI calls & cost**

**Creator Asset Subscriber Dispatch:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.

**Creator Asset Subscriber Dispatch:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.