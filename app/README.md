# W2D3 — Containerized Model Serving

## Overview

In W2D3, I containerized an AI model serving application and deployed it as a CPU-based Docker image.

The service uses **FastAPI + Uvicorn** to serve the `Qwen/Qwen2.5-0.5B-Instruct` model through HTTP endpoints.

The main goal was to build a reproducible container that can be pulled from a registry, started with a persistent Hugging Face cache, and verified through health and inference requests.

## Architecture

The serving stack consists of:

* **FastAPI** — API framework
* **Uvicorn** — ASGI server
* **Transformers** — model loading and inference
* **Qwen/Qwen2.5-0.5B-Instruct** — language model
* **Docker** — containerization
* **Hugging Face cache volume** — persistent model weights

The model weights are stored in a Docker volume instead of being included inside the image.

## Docker Image

The production image was built using:

```bash
docker build -t amalk54/aidc-serving:cpu-v1 .
```

Image:

```text
amalk54/aidc-serving:cpu-v1
```

The image uses a lightweight Python base image and runs the application with Uvicorn.

## Running the Container

The container is started with a persistent Hugging Face cache:

```bash
docker run -d --name serving -p 8000:8000 \
  -v hf-cache:/home/app/.cache/huggingface \
  amalk54/aidc-serving:cpu-v1
```

The service listens on:

```text
http://localhost:8000
```

## Health Check

The service provides a `/health` endpoint:

```bash
curl -s http://localhost:8000/health
```

Expected response:

```json
{"status":"ok","model":"Qwen/Qwen2.5-0.5B-Instruct"}
```

This confirms that the API is running and the model is ready.

**[IMAGE 1 — Screenshot showing the `/health` request and the `{"status":"ok",...}` response.]**

## Chat Completion Test

The model can be accessed through an OpenAI-compatible chat completion endpoint:

```bash
curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen2.5-0.5B-Instruct","messages":[{"role":"user","content":"Say hi."}],"max_tokens":16}'
```

The endpoint returned a successful `chat.completion` response with generated content.

Example:

```json
{
  "object": "chat.completion",
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      }
    }
  ]
}
```

**[IMAGE 2 — Screenshot showing the successful `/v1/chat/completions` request and response.]**

## Verification

The provided `verify.sh` script was used to perform an end-to-end verification.

Command:

```bash
IMAGE=amalk54/aidc-serving:cpu-v1 ./verify.sh
```

The verifier:

1. Removes any existing local copy of the image.
2. Pulls the image from the registry.
3. Starts a fresh container.
4. Uses the `hf-cache` volume.
5. Waits for `/health` to return HTTP 200.
6. Sends a real chat completion request.
7. Cleans up the verification container.

Verification result:

```text
image: amalk54/aidc-serving:cpu-v1
health: 200
completion: ok
GREEN CHECK: PASS
```

**[IMAGE 3 — Screenshot showing the complete `verify.sh` output ending with `GREEN CHECK: PASS`.]**

## Naive vs Optimized Image

A `Dockerfile.naive` was also tested as a baseline.

The naive image used:

```dockerfile
FROM python:3.11
```

and installed the full requirements directly.

During the build, PyTorch pulled a large set of CUDA-related dependencies even though the service was intended to run on CPU. The build took a long time and eventually failed while downloading a large CUDA dependency.

The production Dockerfile was designed to avoid this unnecessary overhead and produce a more suitable CPU serving image.

## Result

The final serving image successfully:

* Builds with Docker
* Starts as a container
* Loads the Qwen model
* Exposes a health endpoint
* Serves chat completions
* Uses a persistent Hugging Face cache
* Passes the provided end-to-end verifier

Final verification status:

**GREEN CHECK: PASS**
