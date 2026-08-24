
# W2D2 - Containerized LLM Serving

## Overview

In W2D2, I built and containerized a small CPU-based LLM serving service using FastAPI and Docker.

The service exposes an OpenAI-compatible API for the model:

`Qwen/Qwen2.5-0.5B-Instruct`

![Models](screenshots/W2D2-2.png)

## Environment

- Python 3.11
- Docker 29.7.2
- CPU inference
- Base image: `python:3.11-slim`

## API Endpoints

### GET /health

Used to check that the service and model are ready.

Example response:

```json
{
  "status": "ok",
  "model": "Qwen/Qwen2.5-0.5B-Instruct"
}
````

![Health endpoint](screenshots/W2D2-1.png)

### GET /v1/models

Returns the model served by the API.

The endpoint was tested successfully and returned:

```text
Qwen/Qwen2.5-0.5B-Instruct
```
![Models endpoint](screenshots/W2D2-3.png)

### POST /v1/chat/completions

Provides non-streaming chat completions using the served model.

Example request:

```json
{
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "messages": [
    {
      "role": "user",
      "content": "Say hello in one word."
    }
  ],
  "max_tokens": 16
}
```

Example response:

```text
Hello.
```
![Models endpoint](screenshots/W2D2-3.png)

The response also includes the completion ID, model, finish reason, and token usage.

## OpenAI Client Test

The service was also tested using the official OpenAI Python client by changing the `base_url` to the local service:

```python
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)
```

The client successfully received a response from the local model.

## Docker

The application was built as a Docker image:

```bash
docker build -t w2d2-serving .
```

The container was then started with:

```bash
docker run --rm -p 8000:8000 --name w2d2-serving w2d2-serving
```

The service successfully started on:

```text
http://localhost:8000
```

## Verification

The following endpoints were tested successfully:

* `/health`
* `/v1/models`
* `/v1/chat/completions`

![Chat completion](screenshots/W2D2-4.png)
The service was also verified using the provided `verify.py` script.
