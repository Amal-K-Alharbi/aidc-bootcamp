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



## Naive vs Optimized Image

A `Dockerfile.naive` was built as a baseline to measure the impact of the optimizations.

The naive image used:

```dockerfile
FROM python:3.11
```

and installed the full requirements directly.

The final measured image sizes were:

| Image          |    Size |
| -------------- | ------: |
| Naive build    | 16.5 GB |
| Slim CPU build | 1.61 GB |

The optimized image is approximately 14.89 GB smaller.

The main optimizations were:

Using python:3.11-slim instead of python:3.11
Installing the CPU-only PyTorch wheel using the PyTorch CPU index
Using pip --no-cache-dir
Using .dockerignore to exclude unnecessary files from the build context

The naive image was much larger mainly because the default PyTorch installation pulled CUDA-related dependencies that were unnecessary for this CPU-only serving stack.

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
