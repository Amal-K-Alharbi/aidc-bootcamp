"""serving-stack: the FastAPI service (week 2, CPU, tiny model).

This is the starter. GET /health is done for you and works as soon as the model
loads: treat it as the worked example. Your job is the two routes marked TODO.
Correctness before speed. The model runs on CPU this week; do not add a GPU.

Run it:
    uvicorn main:app --host 0.0.0.0 --port 8000

Model: Qwen/Qwen2.5-0.5B-Instruct (about 0.5B params; loads on CPU in seconds
once cached). The first ever load downloads weights; the prep-week verify-env
pass pre-seeded the Hugging Face cache, so a cached load is fast.
"""

from __future__ import annotations

import os
import time
import uuid

import torch
from fastapi import FastAPI, Header, HTTPException
from transformers import AutoModelForCausalLM, AutoTokenizer

from schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    HealthResponse,
    ModelList,
)


MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
API_KEY = os.environ.get("API_KEY", "")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "256"))


if not API_KEY:
    print(
        "WARNING: API_KEY is not set. "
        "/v1 endpoints are running WITHOUT authentication."
    )


app = FastAPI(title="serving-stack", version="wk2")


def require_api_key(authorization: str | None) -> None:
    """Require a valid Bearer token when API_KEY is configured."""
    if not API_KEY:
        return

    expected = f"Bearer {API_KEY}"

    if authorization != expected:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )


# ---------------------------------------------------------------------------
# Load model once at import time. CPU only this week.
# ---------------------------------------------------------------------------

print(f"loading {MODEL_ID} on cpu ...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
)

model.to("cpu")
model.eval()

print("model ready")


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness and readiness.

    Contract: returns 200 with {"status": "ok", "model": "<id>"} once the model
    is loaded. Kubernetes probes (week 4) and the agentic client's retry logic
    (weeks 4 to 6) call this. It must be cheap and must not run the model.
    """
    return HealthResponse(
        status="ok",
        model=MODEL_ID,
    )


# ---------------------------------------------------------------------------
# GET /v1/models
# ---------------------------------------------------------------------------

@app.get("/v1/models", response_model=ModelList)
def list_models(
    authorization: str | None = Header(default=None),
) -> ModelList:
    """List the served model id(s).

    Contract (OpenAI-compatible):
      response body: {"object": "list", "data": [ {ModelCard}, ... ]}
      each ModelCard has: id (== MODEL_ID), object == "model", created (unix
      seconds), owned_by.
    Week 2 serves exactly one model, so data has one entry: MODEL_ID.
    """

    require_api_key(authorization)

    return ModelList(
        object="list",
        data=[
            {
                "id": MODEL_ID,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "serving-stack",
            }
        ],
    )


# ---------------------------------------------------------------------------
# POST /v1/chat/completions
# ---------------------------------------------------------------------------

@app.post(
    "/v1/chat/completions",
    response_model=ChatCompletionResponse,
)
def chat_completions(
    req: ChatCompletionRequest,
    authorization: str | None = Header(default=None),
) -> ChatCompletionResponse:
    """Run the model over the messages and return an OpenAI-compatible completion.

    Contract (non-streaming, the week-2 target):
      request:  ChatCompletionRequest (model, messages[], max_tokens, temperature)
      response: ChatCompletionResponse with
        id            a unique string, e.g. "chatcmpl-" + uuid4().hex
        object        "chat.completion"
        created       int(time.time())
        model         req.model
        choices[0]    Choice(message=ResponseMessage(role="assistant",
                        content=<generated text>), finish_reason="stop" or "length")
        usage         Usage(prompt_tokens, completion_tokens, total_tokens),
                        all non-negative and total == prompt + completion
    """

    require_api_key(authorization)

    # Apply the hard maximum configured by MAX_TOKENS.
    max_tokens = min(req.max_tokens, MAX_TOKENS)

    input_ids = tokenizer.apply_chat_template(
        [m.model_dump() for m in req.messages],
        add_generation_prompt=True,
        return_tensors="pt",
    )

    prompt_tokens = input_ids.shape[1]

    with torch.no_grad():
        out = model.generate(
            input_ids,
            max_new_tokens=max_tokens,
            do_sample=req.temperature > 0,
            temperature=(
                req.temperature
                if req.temperature > 0
                else None
            ),
        )

    new_tokens = out[0][prompt_tokens:]
    completion_tokens = len(new_tokens)

    text = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True,
    )

    finish_reason = (
        "length"
        if completion_tokens >= max_tokens
        else "stop"
    )

    return ChatCompletionResponse(
        id="chatcmpl-" + uuid.uuid4().hex,
        object="chat.completion",
        created=int(time.time()),
        model=req.model,
        choices=[
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": text,
                },
                "finish_reason": finish_reason,
            }
        ],
        usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    )

